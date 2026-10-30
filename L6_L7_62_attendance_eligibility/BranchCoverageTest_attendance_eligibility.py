
import pytest

from attendance_eligibility import (
    attendance_percent,
    exam_eligibility,
    attendance_warning,
)


# Attendance percentage decision branches

def test_attendance_percent_valid():
    assert attendance_percent(30, 40, 0) == 75


def test_attendance_percent_invalid_total():
    with pytest.raises(ValueError, match="invalid total"):
        attendance_percent(30, 0, 0)


def test_attendance_percent_negative_attended():
    with pytest.raises(ValueError, match="invalid attended"):
        attendance_percent(-1, 40, 0)


def test_attendance_percent_exceeds_total():
    with pytest.raises(ValueError, match="invalid attended"):
        attendance_percent(41, 40, 0)


def test_medical_leave_exceeds_limit():
    assert attendance_percent(30, 40, 8) == 87


def test_credited_attendance_exceeds_total():
    assert attendance_percent(38, 40, 5) == 100


# Exam eligibility decision branches

def test_exam_fees_unpaid():
    assert exam_eligibility(80, False, False) == "fees pending"


def test_exam_eligible_at_75():
    assert exam_eligibility(75, False, True) == "eligible"


def test_exam_condonation_approved():
    assert exam_eligibility(70, True, True) == "eligible"


def test_exam_condonation_required():
    assert exam_eligibility(70, False, True) == "condonation required"


def test_exam_detained():
    assert exam_eligibility(64, False, True) == "detained"


# Attendance warning decision branches

def test_no_attendance_warning():
    assert attendance_warning(85, 5) is None


def test_reminder_warning():
    assert attendance_warning(80, 5) == "reminder"


def test_critical_warning():
    assert attendance_warning(74, 5) == "critical"


def test_final_notice():
    assert attendance_warning(74, 4) == "final notice"
