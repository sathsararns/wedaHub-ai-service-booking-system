"""Manual check; run explicitly with python -m from the service root."""


def main():
    import asyncio

    from experiments.legacy.database import db


    async def test():
        print(await db.list_collection_names())


    asyncio.run(test())


if __name__ == "__main__":
    main()
