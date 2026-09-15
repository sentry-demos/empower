from typing import Any

from app.session import OMITTED_TOOL_RESULT, ChatSession, trim_tool_outputs


def turn(user: str, call_id: str, tool: str, output: str, reply: str) -> list[Any]:
    """One turn's worth of history, in the shape to_input_list() produces."""
    return [
        {"role": "user", "content": user},
        {
            "arguments": "{}",
            "call_id": call_id,
            "id": "__fake_id__",
            "name": tool,
            "type": "function_call",
        },
        {"call_id": call_id, "output": output, "type": "function_call_output"},
        {
            "id": "__fake_id__",
            "content": [{"annotations": [], "text": reply, "type": "output_text"}],
            "role": "assistant",
            "status": "completed",
            "type": "message",
        },
    ]


# Sized like the real thing: a live search_products result is ~1.3KB and a cart
# ~1.5KB, which is what makes them worth collapsing at all.
PRODUCTS_JSON = (
    '{"products": [{"id": 3, "title": "Plant Mood", "description": "The mood ring'
    ' for plants.", "price": 155, "img": "https://storage.googleapis.com/'
    'application-monitoring/plant-mood.png", "imgcropped": "https://storage.'
    'googleapis.com/application-monitoring/plant-mood-cropped.png"}], "count": 1}'
)
CART_JSON = (
    '{"cart": {"items": [{"id": 3, "title": "Plant Mood", "description": "The mood'
    ' ring for plants.", "price": 155, "img": "https://storage.googleapis.com/'
    'application-monitoring/plant-mood.png"}], "quantities": {"3": 1}, "total":'
    " 155}}"
)

HISTORY = [
    *turn(
        "Show me plants under $200",
        "call_1",
        "ask_product_agent",
        PRODUCTS_JSON,
        "Here are plants under $200.",
    ),
    *turn(
        "Add one of each to the cart",
        "call_2",
        "ask_checkout_agent",
        CART_JSON,
        "I added one of each to your cart.",
    ),
]


def outputs(history: list[Any]) -> list[str]:
    return [
        item["output"] for item in history if item.get("type") == "function_call_output"
    ]


def test_keeps_the_latest_tool_result_and_collapses_the_rest() -> None:
    first, second = outputs(trim_tool_outputs(HISTORY))

    assert first == OMITTED_TOOL_RESULT.format(tool="ask_product_agent")
    assert second == CART_JSON


def test_keeps_every_other_item_untouched() -> None:
    trimmed = trim_tool_outputs(HISTORY)

    assert len(trimmed) == len(HISTORY)
    for before, after in zip(HISTORY, trimmed):
        if before.get("type") != "function_call_output":
            assert before == after


def test_keeps_a_function_call_output_for_every_function_call() -> None:
    # A function_call whose output has gone missing is rejected by the API, so
    # the trim must never drop one.
    trimmed = trim_tool_outputs(HISTORY)

    calls = {item["call_id"] for item in trimmed if item.get("type") == "function_call"}
    results = {
        item["call_id"]
        for item in trimmed
        if item.get("type") == "function_call_output"
    }
    assert calls == results


def test_never_grows_the_history() -> None:
    # A failed coupon or a rejected purchase is a sentence, not a JSON blob, and
    # is shorter than the note explaining its absence. Collapsing it would cost
    # bytes and lose detail.
    short = "Provided coupon code has expired."
    history = [
        *turn("Apply Coupon", "call_1", "ask_checkout_agent", short, "It expired."),
        *turn("Checkout", "call_2", "ask_checkout_agent", CART_JSON, "Checking out."),
    ]

    assert outputs(trim_tool_outputs(history)) == [short, CART_JSON]


def test_does_not_mutate_the_history_it_was_given() -> None:
    # The items come out of the SDK's run result, which still holds them.
    trim_tool_outputs(HISTORY)

    assert outputs(HISTORY) == [PRODUCTS_JSON, CART_JSON]


def test_keep_zero_collapses_everything() -> None:
    # Guards the -0 == 0 slice: positions[:-0] would be empty and trim nothing.
    trimmed = trim_tool_outputs(HISTORY, keep=0)

    assert outputs(trimmed) == [
        OMITTED_TOOL_RESULT.format(tool="ask_product_agent"),
        OMITTED_TOOL_RESULT.format(tool="ask_checkout_agent"),
    ]


def test_keeping_more_turns_than_exist_collapses_nothing() -> None:
    assert trim_tool_outputs(HISTORY, keep=5) == HISTORY


def test_names_an_orphaned_tool_result_generically() -> None:
    # Defensive: a result whose function_call isn't in the window still has to
    # produce a sentence rather than "None ran earlier".
    orphan = [
        {"call_id": "gone", "output": PRODUCTS_JSON, "type": "function_call_output"},
        *HISTORY,
    ]

    assert outputs(trim_tool_outputs(orphan))[0] == OMITTED_TOOL_RESULT.format(
        tool="A specialist"
    )


def test_passes_non_dict_items_through() -> None:
    assert trim_tool_outputs(["not a dict"]) == ["not a dict"]


def test_is_idempotent() -> None:
    # Every turn re-trims the whole history, so a second pass must be a no-op
    # rather than re-collapsing an already-collapsed note.
    once = trim_tool_outputs(HISTORY)

    assert trim_tool_outputs(once) == once


def test_remember_trims_before_storing() -> None:
    session = ChatSession(conversation_id="test")

    session.remember(HISTORY)

    assert outputs(session.history)[0] == OMITTED_TOOL_RESULT.format(
        tool="ask_product_agent"
    )
