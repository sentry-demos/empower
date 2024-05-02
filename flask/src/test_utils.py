from .utils import *

def test():
    assert yuval("abc") == ""

def test_get_subscription_plan():
    assert get_subscription_plan('monthly') == 'monthly'
    assert get_subscription_plan('annual') == 'annual'
    assert get_subscription_plan('nonexistent_plan') == 'annual'
