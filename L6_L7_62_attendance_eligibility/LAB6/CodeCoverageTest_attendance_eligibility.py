
import pytest

from attendance_eligibility import (
    attendance_percent,
    exam_eligibility,
    attendance_warning,
)


def test_attendance_percent():
    assert attendance_percent(30, 40, 0) == 75


def test_invalid_total():
    with pytest.raises(ValueError):
        attendance_percent(30, 0, 0)


def test_invalid_attended():
    with pytest.raises(ValueError):
        attendance_percent(-1, 40, 0)


def test_medical_leave_limit():
    assert attendance_percent(30, 40, 8) == 87


def test_credited_attendance_limit():
    assert attendance_percent(38, 40, 5) == 100


def test_exam_fees_pending():
    assert exam_eligibility(80, False, False) == "fees pending"


def test_exam_eligible():
    assert exam_eligibility(80, False, True) == "eligible"


def test_exam_condonation_required():
    assert exam_eligibility(70, False, True) == "condonation required"

def test_exam_detained():
    assert exam_eligibility(60, False, True) == "detained"


def test_no_attendance_warning():
    assert attendance_warning(90, 5) is None


def test_critical_warning():
    assert attendance_warning(70, 5) == "critical"


def test_final_notice():
    assert attendance_warning(70, 4) == "final notice"


def test_reminder_warning():
    assert attendance_warning(80, 5) == "reminder"

def test_exam_condonation_approved():
    assert exam_eligibility(70, True, True) == "eligible"