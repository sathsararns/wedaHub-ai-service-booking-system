"""Manual check; run explicitly with python -m from the service root."""


def main():
    from experiments.legacy.booking_agent import get_booking_agent

    result = get_booking_agent().invoke({
        "input": "Book provider 1 tomorrow at 10 AM"
    })

    print(result)


if __name__ == "__main__":
    main()
