"""
Navy Sailor Digital Twin - Synthetic Data Generator
====================================================

Generates realistic synthetic data for ~5,000 active duty enlisted Sailors,
populating all 7 domains plus the personnel event stream.

NO REAL PII. All identifiers, dates, and attributes are randomly generated.

Design principles:
  1. Realistic distributions - paygrade, age, YOS roughly match Navy demographics
  2. Embedded patterns - the data contains *learnable signals* for retention and
     promotion readiness (so our models actually find something meaningful)
  3. Reproducibility - fixed random seed for consistent demos
  4. Source-system fidelity - field names and values mirror real Navy systems

Usage:
    python generate_data.py [--sailors N] [--db-path PATH] [--seed N]
"""

import argparse
import json
import random
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

# =============================================================================
# REFERENCE DATA - mirrors real Navy taxonomies (small subset for POC)
# =============================================================================

# Subset of Navy ratings, focused on a mix of communities
# (is_critical flag drives retention prioritization later)
RATES = [
    # (rate_code, rate_name, community, is_critical)
    ("MM",  "Machinist's Mate",                   "Engineering",   0),
    ("MMN", "Machinist's Mate Nuclear",           "Nuclear",       1),
    ("ETN", "Electronics Tech Nuclear",           "Nuclear",       1),
    ("EMN", "Electrician's Mate Nuclear",         "Nuclear",       1),
    ("CTN", "Cryptologic Technician Networks",    "Cyber",         1),
    ("CTI", "Cryptologic Technician Interpretive","Cyber",         1),
    ("IT",  "Information Systems Technician",     "Cyber",         1),
    ("HM",  "Hospital Corpsman",                  "Medical",       0),
    ("ABF", "Aviation Boatswain (Fuels)",         "Aviation",      0),
    ("ABE", "Aviation Boatswain (Equipment)",     "Aviation",      0),
    ("AT",  "Aviation Electronics Technician",    "Aviation",      0),
    ("AD",  "Aviation Machinist's Mate",          "Aviation",      0),
    ("BM",  "Boatswain's Mate",                   "Surface",       0),
    ("OS",  "Operations Specialist",              "Surface",       0),
    ("FC",  "Fire Controlman",                    "Surface",       0),
    ("STG", "Sonar Technician (Surface)",         "Surface",       0),
    ("STS", "Sonar Technician (Submarine)",       "Submarine",     1),
    ("MT",  "Missile Technician",                 "Submarine",     1),
    ("YN",  "Yeoman",                             "Admin",         0),
    ("PS",  "Personnel Specialist",               "Admin",         0),
    ("LS",  "Logistics Specialist",               "Admin",         0),
    ("MA",  "Master-at-Arms",                     "Security",      0),
]

# NEC codes - small representative subset
NECS = [
    # (nec_code, nec_title, related_rate, is_critical, currency_months)
    ("3354", "Gas Turbine Systems Tech",          "MM",  0, 36),
    ("3364", "Steam Plant Operator",              "MM",  0, 36),
    ("3265", "Naval Nuclear Power Plant Operator","MMN", 1, 24),
    ("3389", "Reactor Operator",                  "ETN", 1, 24),
    ("9701", "Network Security Specialist",       "CTN", 1, 12),
    ("9702", "Cyber Defense Operator",            "CTN", 1, 12),
    ("0000", "General Detail",                    None,  0, None),
    ("8404", "Field Medical Service Tech",        "HM",  1, 24),
    ("L23A", "Aegis Combat System Tech",          "FC",  1, 24),
    ("0950", "Master-at-Arms Advanced",           "MA",  0, 36),
    ("3429", "Aircraft Maintenance Admin",        "AD",  0, 24),
    ("8478", "Independent Duty Corpsman",         "HM",  1, 24),
    ("V13A", "Submarine Sonar Technician",        "STS", 1, 24),
]

# Commands - mix of sea, shore, overseas
COMMANDS = [
    # (command_id, command_name, type, homeport, region, fleet)
    ("N00001", "USS GERALD R FORD CVN-78",        "Sea",      "Norfolk",     "Norfolk",     "Atlantic"),
    ("N00002", "USS NIMITZ CVN-68",               "Sea",      "Bremerton",   "Bremerton",   "Pacific"),
    ("N00003", "USS RONALD REAGAN CVN-76",        "Sea",      "Yokosuka",    "Yokosuka",    "Pacific"),
    ("N00004", "USS BAINBRIDGE DDG-96",           "Sea",      "Norfolk",     "Norfolk",     "Atlantic"),
    ("N00005", "USS HALSEY DDG-97",               "Sea",      "San Diego",   "San Diego",   "Pacific"),
    ("N00006", "USS MICHIGAN SSGN-727",           "Sea",      "Bangor",      "Bangor",      "Pacific"),
    ("N00007", "USS VIRGINIA SSN-774",            "Sea",      "Groton",      "Groton",      "Atlantic"),
    ("N00008", "NAS Oceana",                      "Shore",    "Virginia Beach","Norfolk",   "Atlantic"),
    ("N00009", "NAS North Island",                "Shore",    "San Diego",   "San Diego",   "Pacific"),
    ("N00010", "NAVSTA Norfolk",                  "Shore",    "Norfolk",     "Norfolk",     "Atlantic"),
    ("N00011", "Naval Base San Diego",            "Shore",    "San Diego",   "San Diego",   "Pacific"),
    ("N00012", "NAVSTA Pearl Harbor",             "Shore",    "Pearl Harbor","Pearl Harbor","Pacific"),
    ("N00013", "Recruit Training Command",        "Shore",    "Great Lakes", "Great Lakes", "CNRC"),
    ("N00014", "Naval Cyber Defense Ops Cmd",     "Shore",    "Suffolk",     "Norfolk",     "FCC"),
    ("N00015", "FLENUMMETOC",                     "Shore",    "Monterey",    "San Diego",   "Pacific"),
    ("N00016", "USS THEODORE ROOSEVELT CVN-71",   "Sea",      "San Diego",   "San Diego",   "Pacific"),
    ("N00017", "USS WAYNE E MEYER DDG-108",       "Sea",      "San Diego",   "San Diego",   "Pacific"),
    ("N00018", "Recruiting Command",              "Shore",    "Millington",  "Millington",  "CNRC"),
    ("N00019", "NAVSUP FLC Norfolk",              "Shore",    "Norfolk",     "Norfolk",     "Atlantic"),
    ("N00020", "NIOC Hawaii",                     "Overseas", "Wahiawa",     "Pearl Harbor","FCC"),
]

# Paygrade time-in-rate minimums (months) for advancement eligibility
PAYGRADE_TIR_MIN = {
    "E1": 0,  "E2": 6,  "E3": 9,  "E4": 12, "E5": 36,
    "E6": 36, "E7": 36, "E8": 36, "E9": 36
}
PAYGRADES_ORDER = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"]

# Approximate Navy enlisted paygrade distribution (ratios)
PAYGRADE_DISTRIBUTION = {
    "E1": 0.04, "E2": 0.07, "E3": 0.18, "E4": 0.24, "E5": 0.21,
    "E6": 0.14, "E7": 0.07, "E8": 0.03, "E9": 0.02
}

# Base pay roughly aligned with 2024 pay tables (rounded)
BASE_PAY_BY_PAYGRADE = {
    "E1": 2017, "E2": 2261, "E3": 2378, "E4": 2634, "E5": 2872,
    "E6": 3134, "E7": 3624, "E8": 5215, "E9": 6371
}

# =============================================================================
# DATA GENERATOR
# =============================================================================

class SailorDataGenerator:
    """Generates synthetic but realistic Navy enlisted personnel data."""

    def __init__(self, num_sailors: int = 5000, seed: int = 42):
        self.num_sailors = num_sailors
        self.rng = random.Random(seed)
        self.today = date(2026, 4, 26)
        self.events = []  # accumulated personnel events

    # ---- helpers ----
    def _gen_dod_id(self, idx: int) -> str:
        """Synthetic 10-digit DoD ID. Prefix '999' marks it as synthetic."""
        return f"999{idx:07d}"

    def _gen_uuid(self) -> str:
        return str(uuid.uuid4())[:12]

    def _date_offset(self, base: date, days_min: int, days_max: int) -> date:
        return base + timedelta(days=self.rng.randint(days_min, days_max))

    def _weighted_choice(self, choices_with_weights):
        items = [c[0] for c in choices_with_weights]
        weights = [c[1] for c in choices_with_weights]
        return self.rng.choices(items, weights=weights, k=1)[0]

    def _record_event(self, dod_id: str, event_type: str, event_date: date,
                      source_system: str, payload: Optional[dict] = None,
                      subtype: Optional[str] = None):
        self.events.append({
            "event_id": self._gen_uuid(),
            "dod_id": dod_id,
            "event_type": event_type,
            "event_subtype": subtype,
            "event_date": event_date.isoformat(),
            "source_system": source_system,
            "event_payload": json.dumps(payload) if payload else None,
        })

    # ---- reference data ----
    def insert_reference_data(self, conn: sqlite3.Connection):
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO rate (rate_code, rate_name, community, is_critical) VALUES (?, ?, ?, ?)",
            RATES,
        )
        cur.executemany(
            "INSERT INTO nec (nec_code, nec_title, related_rate, is_critical, typical_currency_months) VALUES (?, ?, ?, ?, ?)",
            NECS,
        )
        cur.executemany(
            "INSERT INTO command (command_id, command_name, command_type, homeport, region, fleet) VALUES (?, ?, ?, ?, ?, ?)",
            COMMANDS,
        )
        conn.commit()

    # ---- billet generation (must precede sailors) ----
    def generate_billets(self, conn: sqlite3.Connection):
        """Generate billets across commands. ~20% will start unfilled (gaps)."""
        billets = []
        billet_id_counter = 1
        # Each command gets 200-400 billets; total ~5000-6000 billets
        for cmd in COMMANDS:
            command_id = cmd[0]
            command_type = cmd[2]
            num_billets = self.rng.randint(200, 400)
            for _ in range(num_billets):
                rate = self.rng.choice(RATES)
                paygrade = self._weighted_choice(list(PAYGRADE_DISTRIBUTION.items()))
                # Critical NEC requirement only for certain rates
                rate_necs = [n for n in NECS if n[2] == rate[0]]
                nec_required = rate_necs[0][0] if rate_necs and self.rng.random() < 0.4 else None
                is_critical = 1 if (rate[3] == 1 and self.rng.random() < 0.4) else 0
                billets.append({
                    "billet_id": f"BIN-{billet_id_counter:06d}",
                    "command_id": command_id,
                    "rate_required": rate[0],
                    "paygrade_required": paygrade,
                    "nec_required": nec_required,
                    "nec_required_secondary": None,
                    "sea_shore": "Sea" if command_type == "Sea" else "Shore",
                    "is_critical": is_critical,
                    "is_filled": 0,  # Will update as sailors get assigned
                })
                billet_id_counter += 1

        cur = conn.cursor()
        for b in billets:
            cur.execute("""
                INSERT INTO billet (billet_id, command_id, rate_required, paygrade_required,
                                    nec_required, nec_required_secondary, sea_shore,
                                    is_critical, is_filled)
                VALUES (:billet_id, :command_id, :rate_required, :paygrade_required,
                        :nec_required, :nec_required_secondary, :sea_shore,
                        :is_critical, :is_filled)
            """, b)
        conn.commit()
        return billets

    # ---- sailor generation ----
    def generate_sailor(self, idx: int, available_billets: list) -> dict:
        """Generate a single Sailor with embedded retention/promotion patterns."""
        dod_id = self._gen_dod_id(idx)

        # Paygrade follows rough distribution
        paygrade = self._weighted_choice(list(PAYGRADE_DISTRIBUTION.items()))
        pg_idx = PAYGRADES_ORDER.index(paygrade)

        # YOS aligned with paygrade (E3 ~= 1-3 yrs, E5 ~= 4-8 yrs, E7 ~= 12-18 yrs, etc.)
        yos_min = {"E1": 0,  "E2": 0,  "E3": 1,  "E4": 2,  "E5": 4,
                   "E6": 7,  "E7": 11, "E8": 16, "E9": 19}[paygrade]
        yos_max = {"E1": 1,  "E2": 2,  "E3": 4,  "E4": 8,  "E5": 12,
                   "E6": 18, "E7": 24, "E8": 28, "E9": 30}[paygrade]
        yos = round(self.rng.uniform(yos_min, yos_max), 1)
        age = int(18 + yos + self.rng.uniform(0, 4))

        enlistment_date = self._date_offset(self.today, -int(yos * 365), -int(yos * 365) + 30)

        # Time in rate (months) - varies by promotion velocity
        # Some Sailors are "fast trackers" (low TIR for paygrade), some "stagnant" (high TIR)
        promotion_velocity = self._weighted_choice([
            ("fast",    0.2),
            ("normal",  0.6),
            ("slow",    0.2),
        ])
        tir_base = PAYGRADE_TIR_MIN[paygrade]
        if promotion_velocity == "fast":
            tir_months = self.rng.randint(max(1, tir_base), tir_base + 12)
        elif promotion_velocity == "normal":
            tir_months = self.rng.randint(tir_base + 6, tir_base + 30)
        else:  # slow
            tir_months = self.rng.randint(tir_base + 24, tir_base + 60)

        # Rate
        rate = self.rng.choice(RATES)

        # Primary NEC - 50% have one tied to their rate
        rate_necs = [n for n in NECS if n[2] == rate[0]]
        primary_nec = rate_necs[0][0] if rate_necs and self.rng.random() < 0.5 else "0000"

        # Marriage and dependents - more likely with higher YOS
        if yos < 3:
            marital_status = self._weighted_choice([("Single", 0.75), ("Married", 0.25)])
        elif yos < 8:
            marital_status = self._weighted_choice([("Single", 0.4), ("Married", 0.55), ("Divorced", 0.05)])
        else:
            marital_status = self._weighted_choice([("Single", 0.2), ("Married", 0.7), ("Divorced", 0.1)])
        num_dependents = 0 if marital_status == "Single" else self.rng.randint(0, 4)
        has_efm = 1 if (num_dependents > 0 and self.rng.random() < 0.06) else 0

        gender = self._weighted_choice([("M", 0.83), ("F", 0.16), ("X", 0.01)])

        # EAOS - typically 4-6 year contracts, may have re-enlisted
        contract_length = self.rng.choice([4, 5, 6])
        # Find next contract end based on enlistment + n*contract_length
        years_since_enlist = (self.today - enlistment_date).days / 365.25
        completed_contracts = int(years_since_enlist / contract_length)
        next_eaos = enlistment_date + timedelta(days=int((completed_contracts + 1) * contract_length * 365.25))
        # Some sailors are within 18 months of EAOS - critical retention window
        if self.rng.random() < 0.25:
            # Force into retention decision window
            next_eaos = self.today + timedelta(days=self.rng.randint(60, 540))

        # Assign to a billet matching their rate/paygrade if possible
        matching_billets = [
            b for b in available_billets
            if b["rate_required"] == rate[0] and b["paygrade_required"] == paygrade and b["is_filled"] == 0
        ]
        if not matching_billets:
            # Fall back to any unfilled billet of correct paygrade
            matching_billets = [
                b for b in available_billets
                if b["paygrade_required"] == paygrade and b["is_filled"] == 0
            ]
        if matching_billets:
            assigned_billet = self.rng.choice(matching_billets)
            assigned_billet["is_filled"] = 1
            current_command = assigned_billet["command_id"]
            current_billet = assigned_billet["billet_id"]
        else:
            current_command = self.rng.choice(COMMANDS)[0]
            current_billet = None

        sailor = {
            "dod_id": dod_id,
            "rate_code": rate[0],
            "paygrade": paygrade,
            "primary_nec": primary_nec,
            "secondary_nec": None,
            "enlistment_date": enlistment_date.isoformat(),
            "eaos": next_eaos.isoformat(),
            "years_of_service": yos,
            "time_in_rate_months": tir_months,
            "age": age,
            "gender": gender,
            "marital_status": marital_status,
            "num_dependents": num_dependents,
            "has_efm": has_efm,
            "current_command_id": current_command,
            "current_billet_id": current_billet,
            "status": "Active",
            "separation_date": None,
            "separation_reason": None,
            "_promotion_velocity": promotion_velocity,  # internal use
            "_rate_obj": rate,
            "_pg_idx": pg_idx,
        }

        self._record_event(dod_id, "ACCESSION", enlistment_date, "CIRIMS",
                           {"paygrade_at_accession": "E1"})
        return sailor

    # ---- supporting domain data per sailor ----
    def generate_assignment_history(self, sailor: dict) -> list:
        """Generate 1-5 historical assignments per Sailor."""
        assignments = []
        yos = sailor["years_of_service"]
        # Roughly 1 assignment per 3 years
        num_assignments = max(1, int(yos / 3) + self.rng.randint(0, 1))
        enlistment = date.fromisoformat(sailor["enlistment_date"])

        # Build a chain of assignments
        current_date = enlistment
        for i in range(num_assignments):
            tour_length_months = self.rng.choice([24, 30, 36, 42, 48])
            report_date = current_date
            detach_date = current_date + timedelta(days=tour_length_months * 30)
            is_current = (i == num_assignments - 1)
            if is_current:
                detach_date_value = None
                command_id = sailor["current_command_id"]
                billet_id = sailor["current_billet_id"]
            else:
                detach_date_value = detach_date.isoformat()
                command_id = self.rng.choice(COMMANDS)[0]
                billet_id = None  # historical

            cmd_obj = next(c for c in COMMANDS if c[0] == command_id)
            sea_shore = "Sea" if cmd_obj[2] == "Sea" else "Shore"

            assignments.append({
                "assignment_id": self._gen_uuid(),
                "dod_id": sailor["dod_id"],
                "billet_id": billet_id or f"BIN-HIST-{uuid.uuid4().hex[:12]}",
                "command_id": command_id,
                "report_date": report_date.isoformat(),
                "detach_date": detach_date_value,
                "sea_shore": sea_shore,
                "tour_type": "Standard",
                "is_current": 1 if is_current else 0,
            })

            self._record_event(sailor["dod_id"], "REPORT_ABOARD", report_date,
                               "NSIPS", {"command_id": command_id})
            if not is_current:
                self._record_event(sailor["dod_id"], "DETACH", detach_date,
                                   "NSIPS", {"command_id": command_id})
            current_date = detach_date
        return assignments

    def generate_qualifications(self, sailor: dict) -> list:
        """Generate quals/NECs based on YOS and paygrade."""
        quals = []
        yos = sailor["years_of_service"]
        pg_idx = sailor["_pg_idx"]
        enlistment = date.fromisoformat(sailor["enlistment_date"])

        # Number of quals scales with seniority
        num_quals = max(1, int(yos / 2) + pg_idx + self.rng.randint(-1, 2))

        rate_code = sailor["rate_code"]
        # 60% chance Sailor has primary NEC
        if sailor["primary_nec"] != "0000" and self.rng.random() < 0.85:
            nec_obj = next((n for n in NECS if n[0] == sailor["primary_nec"]), None)
            if nec_obj:
                date_earned = self._date_offset(enlistment, 365, 365 * 3)
                currency_months = nec_obj[4]
                expires = date_earned + timedelta(days=currency_months * 30) if currency_months else None
                # Some quals lapse
                is_current = 1 if (expires is None or expires > self.today) else (1 if self.rng.random() < 0.7 else 0)
                quals.append({
                    "qual_id": self._gen_uuid(),
                    "dod_id": sailor["dod_id"],
                    "qual_type": "NEC",
                    "qual_code": nec_obj[0],
                    "qual_title": nec_obj[1],
                    "date_earned": date_earned.isoformat(),
                    "currency_expires": expires.isoformat() if expires else None,
                    "is_current": is_current,
                    "granting_command": self.rng.choice(COMMANDS)[0],
                })
                self._record_event(sailor["dod_id"], "NEC_AWARDED", date_earned,
                                   "NTMPS", {"nec_code": nec_obj[0]})

        # Add PQS quals (Personnel Qualification Standards)
        pqs_codes = ["301-DC", "302-3M", "303-Watch", "304-EOOW", "305-OOD"]
        for _ in range(min(num_quals, len(pqs_codes))):
            pqs = self.rng.choice(pqs_codes)
            date_earned = self._date_offset(enlistment, 180, max(365, int(yos * 365)))
            quals.append({
                "qual_id": self._gen_uuid(),
                "dod_id": sailor["dod_id"],
                "qual_type": "PQS",
                "qual_code": pqs,
                "qual_title": f"PQS {pqs}",
                "date_earned": date_earned.isoformat(),
                "currency_expires": None,
                "is_current": 1,
                "granting_command": self.rng.choice(COMMANDS)[0],
            })
        return quals

    def generate_fitreps(self, sailor: dict) -> list:
        """Generate FITREP history. Promotion velocity affects trait avgs."""
        fitreps = []
        yos = sailor["years_of_service"]
        velocity = sailor["_promotion_velocity"]
        # E4 and below get evals less formally; we'll generate from E4+
        if sailor["paygrade"] in ("E1", "E2", "E3"):
            return fitreps
        num_fitreps = min(int(yos), 8)  # cap
        period_end = self.today
        for _ in range(num_fitreps):
            period_start = period_end - timedelta(days=365)
            # Trait avg correlated with promotion velocity
            if velocity == "fast":
                trait_avg = round(self.rng.uniform(4.2, 4.9), 2)
                promotion_rec = self._weighted_choice([("EP", 0.4), ("MP", 0.4), ("PP", 0.2)])
            elif velocity == "normal":
                trait_avg = round(self.rng.uniform(3.5, 4.4), 2)
                promotion_rec = self._weighted_choice([("MP", 0.3), ("PP", 0.5), ("P", 0.2)])
            else:  # slow
                trait_avg = round(self.rng.uniform(2.8, 3.8), 2)
                promotion_rec = self._weighted_choice([("PP", 0.3), ("P", 0.5), ("SP", 0.2)])
            fr = {
                "fitrep_id": self._gen_uuid(),
                "dod_id": sailor["dod_id"],
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "paygrade_at_eval": sailor["paygrade"],
                "trait_avg": trait_avg,
                "promotion_recommendation": promotion_rec,
                "summary_group_size": self.rng.randint(5, 25),
                "summary_group_avg": round(trait_avg + self.rng.uniform(-0.3, 0.3), 2),
                "is_competitive": 1,
            }
            fitreps.append(fr)
            self._record_event(sailor["dod_id"], "FITREP_SUBMITTED", period_end,
                               "NSIPS-BOL", {"trait_avg": trait_avg, "rec": promotion_rec})
            period_end = period_start
        return fitreps

    def generate_advancement_exams(self, sailor: dict) -> list:
        """Past advancement exams. Higher scores -> faster promotion typically."""
        exams = []
        velocity = sailor["_promotion_velocity"]
        pg_idx = sailor["_pg_idx"]
        # Each paygrade transition E4-E6 typically had an exam
        for target_idx in range(min(4, pg_idx + 1), min(7, pg_idx + 1)):
            if target_idx >= len(PAYGRADES_ORDER):
                break
            target_pg = PAYGRADES_ORDER[target_idx]
            if velocity == "fast":
                score = self.rng.randint(65, 85)
            elif velocity == "normal":
                score = self.rng.randint(50, 70)
            else:
                score = self.rng.randint(35, 60)
            advanced = 1 if (target_idx <= pg_idx and self.rng.random() < 0.85) else 0
            exam_date = self._date_offset(self.today, -int(sailor["years_of_service"] * 365), -180)
            exams.append({
                "exam_id": self._gen_uuid(),
                "dod_id": sailor["dod_id"],
                "exam_cycle": f"{exam_date.year}-Cycle-{1 if exam_date.month <= 6 else 2}",
                "target_paygrade": target_pg,
                "standard_score": score,
                "passed": 1 if score >= 50 else 0,
                "advanced": advanced,
                "exam_date": exam_date.isoformat(),
            })
        return exams

    def generate_pay_record(self, sailor: dict) -> dict:
        paygrade = sailor["paygrade"]
        base_pay = BASE_PAY_BY_PAYGRADE[paygrade]
        bah = self.rng.randint(1500, 3500) if sailor["marital_status"] != "Single" else self.rng.randint(0, 1200)
        bas = 460
        # Sea pay if currently on a sea command
        cmd_obj = next((c for c in COMMANDS if c[0] == sailor["current_command_id"]), None)
        sea_pay = self.rng.randint(150, 400) if cmd_obj and cmd_obj[2] == "Sea" else 0
        special_pay = self.rng.randint(200, 600) if sailor["_rate_obj"][3] == 1 else 0

        # SRB eligibility - active for critical rates approaching reenlistment
        srb_zone = None
        srb_mult = None
        srb_eligible_until = None
        eaos = date.fromisoformat(sailor["eaos"])
        months_to_eaos = (eaos - self.today).days / 30
        yos = sailor["years_of_service"]
        if sailor["_rate_obj"][3] == 1 and 0 < months_to_eaos < 18:
            if yos < 6:
                srb_zone = "A"
                srb_mult = self.rng.choice([2.0, 4.0, 6.0])
            elif yos < 10:
                srb_zone = "B"
                srb_mult = self.rng.choice([1.5, 3.0, 4.5])
            elif yos < 14:
                srb_zone = "C"
                srb_mult = self.rng.choice([1.0, 2.0, 3.0])
            srb_eligible_until = eaos.isoformat()

        return {
            "dod_id": sailor["dod_id"],
            "base_pay_monthly": base_pay,
            "bah_monthly": bah,
            "bas_monthly": bas,
            "sea_pay_monthly": sea_pay,
            "special_pay_monthly": special_pay,
            "srb_zone": srb_zone,
            "srb_multiplier": srb_mult,
            "srb_eligible_until": srb_eligible_until,
            "last_updated": self.today.isoformat(),
        }

    def generate_medical_status(self, sailor: dict) -> dict:
        # Most are deployable; ~12% non-deployable
        is_deployable = 1 if self.rng.random() < 0.88 else 0
        pha_date = self._date_offset(self.today, -400, -30)
        pha_due = pha_date + timedelta(days=365)
        dental_class = self._weighted_choice([(1, 0.45), (2, 0.40), (3, 0.13), (4, 0.02)])
        if dental_class == 4:
            is_deployable = 0
        deployment_limit_until = None
        deployment_limit_reason = None
        if not is_deployable:
            deployment_limit_until = self._date_offset(self.today, 30, 365).isoformat()
            deployment_limit_reason = self.rng.choice([
                "Dental Class 4", "Pending Med Eval", "Profile/Limited Duty",
                "Pregnancy Postpartum", "Vision Waiver Pending"
            ])
        return {
            "dod_id": sailor["dod_id"],
            "pha_date": pha_date.isoformat(),
            "pha_due_date": pha_due.isoformat(),
            "dental_class": dental_class,
            "immunizations_current": 1 if self.rng.random() < 0.93 else 0,
            "is_deployable": is_deployable,
            "deployment_limit_until": deployment_limit_until,
            "deployment_limit_reason": deployment_limit_reason,
            "last_updated": self.today.isoformat(),
        }

    def generate_education(self, sailor: dict) -> list:
        """Most enlisted have HS; some pursue degrees with TA."""
        records = []
        yos = sailor["years_of_service"]
        # Base: HS diploma at accession
        records.append({
            "education_id": self._gen_uuid(),
            "dod_id": sailor["dod_id"],
            "degree_level": "HS",
            "school_name": "High School",
            "completion_date": (date.fromisoformat(sailor["enlistment_date"]) - timedelta(days=180)).isoformat(),
            "used_tuition_assistance": 0,
            "is_completed": 1,
        })
        # Higher YOS sailors more likely to have college
        if yos > 5 and self.rng.random() < 0.4:
            level = self._weighted_choice([("Some College", 0.5), ("AA", 0.3), ("BA", 0.2)])
            records.append({
                "education_id": self._gen_uuid(),
                "dod_id": sailor["dod_id"],
                "degree_level": level,
                "school_name": self.rng.choice(["UMUC", "Excelsior College", "Park University", "ASU Online"]),
                "completion_date": self._date_offset(self.today, -int(yos * 365), -90).isoformat(),
                "used_tuition_assistance": 1,
                "is_completed": 1 if level != "Some College" else 0,
            })
        return records

    def generate_accession(self, sailor: dict) -> dict:
        # ASVAB scores - higher scores correlated with critical rate eligibility
        if sailor["_rate_obj"][3] == 1:
            afqt = self.rng.randint(70, 99)
        else:
            afqt = self.rng.randint(35, 85)
        return {
            "dod_id": sailor["dod_id"],
            "asvab_afqt": afqt,
            "asvab_gs": self.rng.randint(45, 85),
            "asvab_ar": self.rng.randint(45, 85),
            "asvab_mk": self.rng.randint(45, 85),
            "asvab_el": self.rng.randint(45, 85),
            "asvab_mc": self.rng.randint(45, 85),
            "accession_source": self._weighted_choice([("Active", 0.92), ("Prior Service", 0.06), ("Reserve", 0.02)]),
            "enlistment_program": "Nuke" if sailor["_rate_obj"][2] == "Nuclear" else "Cyber" if sailor["_rate_obj"][2] == "Cyber" else "GENDET",
            "contract_term_years": self.rng.choice([4, 5, 6]),
            "accession_date": sailor["enlistment_date"],
            "boot_camp_grad_date": (date.fromisoformat(sailor["enlistment_date"]) + timedelta(days=63)).isoformat(),
            "a_school_grade": round(self.rng.uniform(2.5, 4.0), 2),
        }

    # ---- main run ----
    def run(self, db_path: str):
        """Generate everything and write to SQLite."""
        # Initialize DB with schema
        schema_path = Path(__file__).parent / "schema.sql"
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_path.read_text())
        print(f"  Schema applied to {db_path}")

        self.insert_reference_data(conn)
        print(f"  Reference data inserted: {len(RATES)} rates, {len(NECS)} NECs, {len(COMMANDS)} commands")

        billets = self.generate_billets(conn)
        print(f"  Billets generated: {len(billets):,}")

        cur = conn.cursor()
        sailors_data = []
        all_assignments = []
        all_quals = []
        all_fitreps = []
        all_exams = []
        all_pay = []
        all_medical = []
        all_education = []
        all_accession = []

        for i in range(self.num_sailors):
            s = self.generate_sailor(i + 1, billets)
            sailors_data.append(s)
            all_assignments.extend(self.generate_assignment_history(s))
            all_quals.extend(self.generate_qualifications(s))
            all_fitreps.extend(self.generate_fitreps(s))
            all_exams.extend(self.generate_advancement_exams(s))
            all_pay.append(self.generate_pay_record(s))
            all_medical.append(self.generate_medical_status(s))
            all_education.extend(self.generate_education(s))
            all_accession.append(self.generate_accession(s))
            if (i + 1) % 1000 == 0:
                print(f"  Sailors generated: {i+1:,}/{self.num_sailors:,}")

        # Insert sailors (strip internal-use fields)
        sailor_cols = ["dod_id", "rate_code", "paygrade", "primary_nec", "secondary_nec",
                       "enlistment_date", "eaos", "years_of_service", "time_in_rate_months",
                       "age", "gender", "marital_status", "num_dependents", "has_efm",
                       "current_command_id", "current_billet_id", "status",
                       "separation_date", "separation_reason"]
        for s in sailors_data:
            cur.execute(
                f"INSERT INTO sailor ({','.join(sailor_cols)}) VALUES ({','.join('?'*len(sailor_cols))})",
                tuple(s[c] for c in sailor_cols)
            )

        # Update billet is_filled based on sailor assignments
        cur.execute("UPDATE billet SET is_filled = 1 WHERE billet_id IN (SELECT current_billet_id FROM sailor WHERE current_billet_id IS NOT NULL)")

        # Insert placeholder billets for historical assignments (real Navy data
        # has this property too: old billets get archived/removed from TFMMS,
        # but assignment history references them). We create lightweight stubs.
        historical_billet_ids = set()
        for a in all_assignments:
            if a["billet_id"].startswith("BIN-HIST-"):
                historical_billet_ids.add((a["billet_id"], a["command_id"], a["sea_shore"]))
        for bid, cid, sea_shore in historical_billet_ids:
            cur.execute("""
                INSERT INTO billet (billet_id, command_id, rate_required, paygrade_required,
                                    nec_required, nec_required_secondary, sea_shore,
                                    is_critical, is_filled)
                VALUES (?, ?, 'BM', 'E4', NULL, NULL, ?, 0, 0)
            """, (bid, cid, sea_shore))

        def bulk(table, rows):
            if not rows:
                return
            cols = list(rows[0].keys())
            sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(':'+c for c in cols)})"
            cur.executemany(sql, rows)

        bulk("assignment", all_assignments)
        bulk("qualification", all_quals)
        bulk("fitrep", all_fitreps)
        bulk("advancement_exam", all_exams)
        bulk("pay_record", all_pay)
        bulk("medical_status", all_medical)
        bulk("education_record", all_education)
        bulk("accession", all_accession)
        bulk("personnel_event", self.events)

        conn.commit()
        print(f"\nGeneration complete:")
        print(f"  Sailors:           {len(sailors_data):,}")
        print(f"  Assignments:       {len(all_assignments):,}")
        print(f"  Qualifications:    {len(all_quals):,}")
        print(f"  FITREPs:           {len(all_fitreps):,}")
        print(f"  Advancement exams: {len(all_exams):,}")
        print(f"  Pay records:       {len(all_pay):,}")
        print(f"  Medical statuses:  {len(all_medical):,}")
        print(f"  Education records: {len(all_education):,}")
        print(f"  Accession records: {len(all_accession):,}")
        print(f"  Personnel events:  {len(self.events):,}")
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Generate Navy Digital Twin synthetic data")
    parser.add_argument("--sailors", type=int, default=5000, help="Number of Sailors (default: 5000)")
    parser.add_argument("--db-path", type=str, default="../data/navy_dt.db", help="Output SQLite path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    db_path = Path(args.db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
        print(f"Removed existing database at {db_path}")

    print(f"\nGenerating Navy Digital Twin synthetic data:")
    print(f"  Sailors: {args.sailors:,}")
    print(f"  Output:  {db_path}")
    print(f"  Seed:    {args.seed}\n")

    gen = SailorDataGenerator(num_sailors=args.sailors, seed=args.seed)
    gen.run(str(db_path))
    print(f"\n  Database ready at: {db_path}")


if __name__ == "__main__":
    main()
