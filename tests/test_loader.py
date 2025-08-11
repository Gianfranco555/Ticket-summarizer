from pathlib import Path
from summarizer.loader import Ticket, load_tickets

def test_sample_load():
    sample = Path("sample_data/tiny_demo.csv")
    rows = load_tickets(sample)
    assert len(rows) == 3
    assert rows[0].number == "1"
    assert rows[0].description == "This is a test ticket"
    assert rows[1].number == "2"
    assert rows[1].description == "This is another test ticket"
    assert rows[2].number == "3"
    assert rows[2].description == "This is a third test ticket"


def test_load_tickets_custom_delimiter(tmp_path):
    csv_content = "number;description\n10;custom delim ticket"
    p = tmp_path / "test.csv"
    p.write_text(csv_content)
    tickets = load_tickets(p, delimiter=';')
    assert len(tickets) == 1
    assert tickets[0] == Ticket(
        number="10",
        description="custom delim ticket",
        work_notes="",
        comments="",
        opened_at="",
        resolved_at="",
        closed_at="",
        assignment_group="",
        original_assignment_group="",
    )
