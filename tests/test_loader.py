from pathlib import Path
from datetime import datetime, timezone
from summarizer.loader import Ticket, load_tickets

def test_sample_load():
    sample = Path("sample_data/tiny_demo.csv")
    rows = load_tickets(sample)
    assert len(rows) == 3

    ticket1 = rows[0]
    assert ticket1.number == "1"
    assert ticket1.description == "This is a test ticket"
    assert ticket1.work_notes == ""
    assert ticket1.comments == ""
    assert ticket1.opened_at is None
    assert ticket1.resolved_at is None
    assert ticket1.closed_at is None
    assert ticket1.assignment_group == ""
    assert ticket1.original_assignment_group == ""

    assert rows[1].number == "2"
    assert rows[1].description == "This is another test ticket"
    assert rows[2].number == "3"
    assert rows[2].description == "This is a third test ticket"


def test_load_tickets_custom_delimiter(tmp_path):
    csv_content = "number;description;work_notes;comments;opened_at;resolved_at;closed_at;assignment_group;u_original_assignment_group\n10;custom delim ticket;some notes;some comments;2023-01-01T12:00:00Z;2023-01-02T15:30:00Z;2023-01-03T18:00:00Z;group1;group0"
    p = tmp_path / "test.csv"
    p.write_text(csv_content)
    tickets = load_tickets(p, delimiter=';')
    assert len(tickets) == 1
    assert tickets[0] == Ticket(
        number="10",
        description="custom delim ticket",
        work_notes="some notes",
        comments="some comments",
        opened_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        resolved_at=datetime(2023, 1, 2, 15, 30, 0, tzinfo=timezone.utc),
        closed_at=datetime(2023, 1, 3, 18, 0, 0, tzinfo=timezone.utc),
        assignment_group="group1",
        original_assignment_group="group0",
    )

def test_load_tickets_with_dates(tmp_path):
    csv_content = (
        "number,description,opened_at,resolved_at,closed_at,work_notes,comments,assignment_group,u_original_assignment_group\n"
        "T-1,With date,2023-01-01T12:00:00Z,2023-01-02T15:30:00,not a date,some notes,some comments,group1,group0\n"
        "T-2,No date,,,,,,," # Note the empty and whitespace values
    )
    p = tmp_path / "test_dates.csv"
    p.write_text(csv_content)
    tickets = load_tickets(p)

    assert len(tickets) == 2

    # Check the ticket with valid dates
    ticket1 = tickets[0]
    assert ticket1.number == "T-1"
    assert ticket1.description == "With date"
    assert ticket1.opened_at == datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert ticket1.resolved_at == datetime(2023, 1, 2, 15, 30, 0) # No timezone info, so naive
    assert ticket1.closed_at is None # "not a date" should be parsed as None
    assert ticket1.work_notes == "some notes"
    assert ticket1.comments == "some comments"

    # Check the ticket with no dates and whitespace
    ticket2 = tickets[1]
    assert ticket2.number == "T-2"
    assert ticket2.description == "No date"
    assert ticket2.opened_at is None # Empty value becomes None for dates
    assert ticket2.resolved_at is None # Whitespace value becomes None for dates
    assert ticket2.closed_at is None # Empty value becomes None for dates
    assert ticket2.work_notes == "" # Whitespace is stripped
