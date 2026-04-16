import os 
import datetime

def timebased_model_health(confidence, total_flows):

    def get_days():
        last_trained_phase1 = os.path.getmtime("models/model_phase1.pkl")
        last_trained_phase2 = os.path.getmtime("models/model_phase2.pkl")
        days1 = (datetime.datetime.now() - datetime.datetime.fromtimestamp(last_trained_phase1)).days
        days2 = (datetime.datetime.now() - datetime.datetime.fromtimestamp(last_trained_phase2)).days
        return days1, days2

    # ── Case 1: Not enough data → only time check ──────────────────────────────
    if total_flows < 50:
        try:
            days1, days2 = get_days()
        except FileNotFoundError:
            return "retrain (Models not found)"

        if days1 > 90 or days2 > 90:
            return "retrain (Over 90 days old)"
        else:
            return "healthy (Not enough flows — time check passed)"

    # ── Case 2: Enough data → time + confidence check ──────────────────────────
    try:
        days1, days2 = get_days()
    except FileNotFoundError:
        return "retrain (Models not found)"

    if days1 > 90 or days2 > 90:
        return "retrain (Over 90 days old)"

    if confidence > 0.85:
        return "healthy"
    elif 0.5 <= confidence <= 0.85:
        return "needs observation"
    else:
        return "retrain (Low confidence)"
