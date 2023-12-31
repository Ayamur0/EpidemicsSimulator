def id_factory(page: str):
    def func(_id: str) -> str:
        return f"{page}-{_id}"

    return func
