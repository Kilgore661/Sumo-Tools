from src.validation.rating_persistence.audit import parse_career_rows


def test_parse_career_rows_preserves_rank_and_unranked_statuses():
    html = """
    <table>
      <tr><td><a href='Banzuke.aspx?b=201101#M'>2011.01</a></td><td>M16e</td><td></td></tr>
      <tr><td><a href='Banzuke.aspx?b=201105#Kg'>2011.05</a></td><td>Kg</td><td>Out</td></tr>
      <tr><td><a href='Banzuke.aspx?b=201305#Bg'>2013.05</a></td><td>Bg</td><td></td></tr>
      <tr><td><a href='Banzuke.aspx?b=201307#M'>2013.07</a></td><td>M15w</td><td></td></tr>
    </table>
    """

    rows = parse_career_rows(html, rikishi_id=4980)

    assert [(str(row.date), row.status) for row in rows] == [
        ("2011/01", "M16e"),
        ("2011/05", "Kg"),
        ("2013/05", "Bg"),
        ("2013/07", "M15w"),
    ]
