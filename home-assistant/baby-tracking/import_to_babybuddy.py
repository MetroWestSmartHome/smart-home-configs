#!/usr/bin/env python3
"""
Import Happiest Baby exported data into Baby Buddy.

Features:
- Imports all journal types (feedings, diapers, sleep, pumping, growth)
- Timestamp-based duplicate detection (safe to re-run)
- Dry-run mode for testing
- Progress logging

Configuration:
- Create a .env file with BABYBUDDY_API_KEY and BABYBUDDY_URL
- Or pass --api-key and --base-url on command line

Usage:
    pip install click requests python-dotenv
    python import_to_babybuddy.py --base-url http://YOUR_HA_IP:8000 --api-key YOUR_API_KEY
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import click
import requests

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on env vars or CLI args

# Baby Buddy API endpoints
ENDPOINTS = {
    "children": "/api/children/",
    "feedings": "/api/feedings/",
    "changes": "/api/changes/",  # diapers
    "sleep": "/api/sleep/",
    "pumping": "/api/pumping/",
    "weight": "/api/weight/",
    "height": "/api/height/",
    "head-circumference": "/api/head-circumference/",
}

# Feeding type mapping (Happiest Baby -> Baby Buddy)
FEEDING_TYPE_MAP = {
    "formula": "formula",
    "breastmilk": "breast milk",
    "breast milk": "breast milk",
}


class BabyBuddyClient:
    def __init__(self, base_url: str, api_key: str, dry_run: bool = False):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        }
        self.dry_run = dry_run
        self._cache = {}

    def _get(self, endpoint: str, params: Optional[dict] = None) -> list:
        """GET request to Baby Buddy API with pagination support."""
        url = f"{self.base_url}{endpoint}"
        all_results = []

        while url:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "results" in data:
                all_results.extend(data["results"])
                url = data.get("next")
                params = None  # params already in next URL
            else:
                all_results = data if isinstance(data, list) else [data]
                break

        return all_results

    def _post(self, endpoint: str, data: dict) -> Optional[dict]:
        """POST request to Baby Buddy API."""
        if self.dry_run:
            return {"dry_run": True, **data}

        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_existing_timestamps(self, endpoint: str, child_id: int) -> set:
        """Get set of existing timestamps for duplicate detection."""
        cache_key = f"{endpoint}_{child_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        timestamps = set()
        try:
            entries = self._get(endpoint, {"child": child_id, "limit": 10000})
            for entry in entries:
                # Handle different timestamp field names
                ts = entry.get("start") or entry.get("time") or entry.get("date")
                if ts:
                    # Normalize to UTC minute precision for matching
                    parsed = parse_timestamp(ts)
                    if parsed:
                        # Convert to UTC if timezone-aware
                        if parsed.tzinfo:
                            utc_time = parsed.replace(tzinfo=None) - parsed.utcoffset()
                        else:
                            utc_time = parsed
                        timestamps.add(utc_time.strftime("%Y-%m-%d %H:%M"))
        except Exception as e:
            click.echo(f"  Warning: Could not fetch existing {endpoint}: {e}")

        self._cache[cache_key] = timestamps
        return timestamps

    def get_existing_dates(self, endpoint: str, child_id: int) -> set:
        """Get set of existing dates for duplicate detection (for growth data)."""
        cache_key = f"{endpoint}_{child_id}_dates"
        if cache_key in self._cache:
            return self._cache[cache_key]

        dates = set()
        try:
            entries = self._get(endpoint, {"child": child_id, "limit": 10000})
            for entry in entries:
                date = entry.get("date")
                if date:
                    # Just store the date portion (YYYY-MM-DD)
                    dates.add(date[:10])
        except Exception as e:
            click.echo(f"  Warning: Could not fetch existing {endpoint}: {e}")

        self._cache[cache_key] = dates
        return dates

    def get_existing_sleep_periods(self, child_id: int) -> list:
        """Get list of existing sleep periods (start, end) for overlap detection."""
        cache_key = f"sleep_periods_{child_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        periods = []
        try:
            entries = self._get(ENDPOINTS["sleep"], {"child": child_id, "limit": 10000})
            for entry in entries:
                start = parse_timestamp(entry.get("start"))
                end = parse_timestamp(entry.get("end"))
                if start and end:
                    # Normalize to UTC for comparison
                    if start.tzinfo:
                        start = start.replace(tzinfo=None) - start.utcoffset()
                    if end.tzinfo:
                        end = end.replace(tzinfo=None) - end.utcoffset()
                    periods.append((start, end))
        except Exception as e:
            click.echo(f"  Warning: Could not fetch existing sleep periods: {e}")

        self._cache[cache_key] = periods
        return periods


def parse_timestamp(ts: str) -> Optional[datetime]:
    """Parse various timestamp formats."""
    if not ts:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return None


def timestamp_exists(ts: str, existing: set) -> bool:
    """Check if timestamp already exists (within 1 minute), comparing in UTC."""
    parsed = parse_timestamp(ts)
    if not parsed:
        return False
    # Convert to UTC if timezone-aware
    if parsed.tzinfo:
        utc_time = parsed.replace(tzinfo=None) - parsed.utcoffset()
    else:
        utc_time = parsed
    return utc_time.strftime("%Y-%m-%d %H:%M") in existing


def date_exists(ts: str, existing_dates: set) -> bool:
    """Check if date already exists (for growth data which only has date, not time)."""
    parsed = parse_timestamp(ts)
    if not parsed:
        return False
    return parsed.strftime("%Y-%m-%d") in existing_dates


def sleep_overlaps(start: datetime, end: datetime, existing_periods: list) -> bool:
    """Check if a sleep period overlaps with any existing periods."""
    # Normalize to UTC for comparison
    if start.tzinfo:
        start = start.replace(tzinfo=None) - start.utcoffset()
    if end.tzinfo:
        end = end.replace(tzinfo=None) - end.utcoffset()

    for existing_start, existing_end in existing_periods:
        # Two periods overlap if one starts before the other ends
        if start < existing_end and end > existing_start:
            return True
    return False


def import_bottle_feedings(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import bottle feeding data."""
    if not csv_path.exists():
        return 0, 0

    existing = client.get_existing_timestamps(ENDPOINTS["feedings"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            if not start_time:
                continue

            if timestamp_exists(start_time, existing):
                skipped += 1
                continue

            # Get amount in ml (use metric column)
            amount = row.get("amountMetric") or row.get("amount")
            if amount:
                try:
                    amount = float(amount)
                except ValueError:
                    amount = None

            # Map feeding type
            feed_type = row.get("type", "formula").lower()
            bb_type = FEEDING_TYPE_MAP.get(feed_type, "formula")

            data = {
                "child": child_id,
                "start": start_time,
                "end": start_time,  # Bottle feedings are instant
                "type": bb_type,
                "method": "bottle",
                "amount": amount,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["feedings"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing feeding {start_time}: {e}")

    return imported, skipped


def import_breast_feedings(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import breastfeeding data."""
    if not csv_path.exists():
        return 0, 0

    existing = client.get_existing_timestamps(ENDPOINTS["feedings"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            end_time = row.get("endTime")
            if not start_time:
                continue

            if timestamp_exists(start_time, existing):
                skipped += 1
                continue

            # Determine method from lastUsedBreast
            last_breast = row.get("lastUsedBreast", "").lower()
            if last_breast == "left":
                method = "left breast"
            elif last_breast == "right":
                method = "right breast"
            else:
                method = "both breasts"

            data = {
                "child": child_id,
                "start": start_time,
                "end": end_time or start_time,
                "type": "breast milk",
                "method": method,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["feedings"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing breastfeeding {start_time}: {e}")

    return imported, skipped


def import_diapers(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import diaper change data."""
    if not csv_path.exists():
        return 0, 0

    existing = client.get_existing_timestamps(ENDPOINTS["changes"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            if not start_time:
                continue

            if timestamp_exists(start_time, existing):
                skipped += 1
                continue

            # Parse diaper types
            types = row.get("types", "").lower()
            wet = "pee" in types or "wet" in types
            solid = "poo" in types or "dirty" in types or "solid" in types

            data = {
                "child": child_id,
                "time": start_time,
                "wet": wet,
                "solid": solid,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["changes"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing diaper {start_time}: {e}")

    return imported, skipped


def import_sleep(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import sleep data (using consolidated sleep file).

    IMPORTANT: Uses startTimeFormatted which includes timezone offset (-0500 for EST),
    NOT startTime which has no timezone and would be incorrectly treated as UTC.
    """
    if not csv_path.exists():
        return 0, 0

    existing = client.get_existing_timestamps(ENDPOINTS["sleep"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # CRITICAL: Prefer startTimeFormatted (has timezone like -0500) over
            # startTime (no timezone - would be wrongly treated as UTC)
            start_time = row.get("startTimeFormatted") or row.get("startTime")
            if not start_time:
                continue

            if timestamp_exists(start_time, existing):
                skipped += 1
                continue

            # Calculate end time from duration if not provided
            duration_sec = row.get("stateDuration")
            parsed_start = parse_timestamp(start_time)

            if parsed_start and duration_sec:
                try:
                    end_time = parsed_start + timedelta(seconds=float(duration_sec))
                    # Format with timezone info preserved (use isoformat, not strftime with Z)
                    end_time_str = end_time.isoformat()
                except (ValueError, TypeError):
                    end_time_str = start_time
            else:
                end_time_str = start_time

            data = {
                "child": child_id,
                "start": start_time,
                "end": end_time_str,
            }

            try:
                client._post(ENDPOINTS["sleep"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing sleep {start_time}: {e}")

    return imported, skipped


def import_pumping(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import pumping data."""
    if not csv_path.exists():
        return 0, 0

    existing = client.get_existing_timestamps(ENDPOINTS["pumping"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            end_time = row.get("endTime")
            if not start_time:
                continue

            if timestamp_exists(start_time, existing):
                skipped += 1
                continue

            # Sum left and right amounts (use metric)
            left_amt = float(row.get("left_amountMetric") or 0)
            right_amt = float(row.get("right_amountMetric") or 0)
            total_amount = left_amt + right_amt

            # Baby Buddy pumping requires start/end, not time
            data = {
                "child": child_id,
                "start": start_time,
                "end": end_time or start_time,
                "amount": total_amount if total_amount > 0 else None,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["pumping"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing pumping {start_time}: {e}")

    return imported, skipped


def import_weight(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import weight data."""
    if not csv_path.exists():
        return 0, 0

    # Use date-based deduplication for growth data (Baby Buddy only stores date, not time)
    existing = client.get_existing_dates(ENDPOINTS["weight"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            if not start_time:
                continue

            if date_exists(start_time, existing):
                skipped += 1
                continue

            # Weight in grams (metric)
            weight = row.get("weightMetric")
            if not weight:
                continue

            try:
                weight = float(weight)
            except ValueError:
                continue

            data = {
                "child": child_id,
                "date": start_time[:10],  # Just the date
                "weight": weight,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["weight"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing weight {start_time}: {e}")

    return imported, skipped


def import_height(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import height data."""
    if not csv_path.exists():
        return 0, 0

    # Use date-based deduplication for growth data (Baby Buddy only stores date, not time)
    existing = client.get_existing_dates(ENDPOINTS["height"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            if not start_time:
                continue

            if date_exists(start_time, existing):
                skipped += 1
                continue

            # Height in cm (metric)
            height = row.get("heightMetric")
            if not height:
                continue

            try:
                height = float(height)
            except ValueError:
                continue

            data = {
                "child": child_id,
                "date": start_time[:10],  # Just the date
                "height": height,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["height"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing height {start_time}: {e}")

    return imported, skipped


def import_head_circumference(client: BabyBuddyClient, csv_path: Path, child_id: int) -> tuple[int, int]:
    """Import head circumference data."""
    if not csv_path.exists():
        return 0, 0

    # Use date-based deduplication for growth data (Baby Buddy only stores date, not time)
    existing = client.get_existing_dates(ENDPOINTS["head-circumference"], child_id)
    imported, skipped = 0, 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = row.get("startTime")
            if not start_time:
                continue

            if date_exists(start_time, existing):
                skipped += 1
                continue

            # Circumference in cm (metric)
            circumference = row.get("circumferenceMetric")
            if not circumference:
                continue

            try:
                circumference = float(circumference)
            except ValueError:
                continue

            data = {
                "child": child_id,
                "date": start_time[:10],  # Just the date
                "head_circumference": circumference,
            }

            if row.get("note"):
                data["notes"] = row["note"]

            try:
                client._post(ENDPOINTS["head-circumference"], data)
                imported += 1
            except Exception as e:
                click.echo(f"  Error importing head circumference {start_time}: {e}")

    return imported, skipped


@click.command()
@click.option("--base-url", envvar="BABYBUDDY_URL", required=True, help="Baby Buddy base URL (e.g., http://homeassistant.local:8000)")
@click.option("--api-key", envvar="BABYBUDDY_API_KEY", required=True, help="Baby Buddy API key")
@click.option("--child-id", type=int, default=1, help="Baby Buddy child ID [default: 1]")
@click.option("--data-dir", type=click.Path(exists=True, path_type=Path), default=".", help="Directory containing exported CSV files")
@click.option("--dry-run", is_flag=True, help="Don't actually import, just show what would be imported")
def main(base_url: str, api_key: str, child_id: int, data_dir: Path, dry_run: bool):
    """Import Happiest Baby data into Baby Buddy."""

    if dry_run:
        click.echo("DRY RUN MODE - No data will be imported\n")

    client = BabyBuddyClient(base_url, api_key, dry_run)

    # Verify connection
    click.echo(f"Connecting to Baby Buddy at {base_url}...")
    try:
        children = client._get(ENDPOINTS["children"])
        child = next((c for c in children if c["id"] == child_id), None)
        if not child:
            click.echo(f"Error: Child ID {child_id} not found", err=True)
            sys.exit(1)
        click.echo(f"Connected - importing data for {child['first_name']}\n")
    except Exception as e:
        click.echo(f"Error connecting to Baby Buddy: {e}", err=True)
        sys.exit(1)

    results = []

    # Import each data type
    importers = [
        ("Bottle Feedings", import_bottle_feedings, data_dir / "journals_bottlefeeding.csv"),
        ("Breastfeedings", import_breast_feedings, data_dir / "journals_breastfeeding.csv"),
        ("Diapers", import_diapers, data_dir / "journals_diaper.csv"),
        ("Sleep", import_sleep, data_dir / "journals_sleep.csv"),
        ("Pumping", import_pumping, data_dir / "journals_pumping.csv"),
        ("Weight", import_weight, data_dir / "journals_weight.csv"),
        ("Height", import_height, data_dir / "journals_height.csv"),
        ("Head Circumference", import_head_circumference, data_dir / "journals_head.csv"),
    ]

    for name, importer, csv_path in importers:
        click.echo(f"Importing {name}...")
        if not csv_path.exists():
            click.echo(f"  Skipped (file not found: {csv_path.name})")
            results.append((name, 0, 0, "not found"))
            continue

        imported, skipped = importer(client, csv_path, child_id)
        results.append((name, imported, skipped, "ok"))
        click.echo(f"  Imported: {imported}, Skipped (duplicates): {skipped}")

    # Summary
    click.echo("\n" + "=" * 50)
    click.echo("IMPORT SUMMARY")
    click.echo("=" * 50)

    total_imported = 0
    total_skipped = 0

    for name, imported, skipped, status in results:
        if status == "ok":
            click.echo(f"{name:<20} Imported: {imported:<6} Skipped: {skipped}")
            total_imported += imported
            total_skipped += skipped
        else:
            click.echo(f"{name:<20} {status}")

    click.echo("-" * 50)
    click.echo(f"{'TOTAL':<20} Imported: {total_imported:<6} Skipped: {total_skipped}")

    if dry_run:
        click.echo("\n(Dry run - no data was actually imported)")


if __name__ == "__main__":
    main()
