def test_jominy():
    from metallurgy.jominy import jominy_hardness
    assert jominy_hardness('4140',5) > 40