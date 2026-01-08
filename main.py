from bot import HitplayerBot


def main() -> None:
    with open("token.txt", "r") as f:
        token = f.read().strip()

    HitplayerBot().run(token)


if __name__ == "__main__":
    main()