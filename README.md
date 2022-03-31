# Polaris

Redis-backed FIFO message queue implementation that can hook into a discord bot written with hikari-lightbulb. This
is eventually intended to be the backend communication between a bot and a web dashboard.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Polaris.

```bash
pip install git+https://github.com/tandemdude/lightbulb-ext-polaris.git
```

## Usage

```python
# Receiving messages
import lightbulb
from lightbulb.ext import polaris

bot = lightbulb.BotApp(...)
bot.d.polaris = polaris.BotClient(bot, "redis://your_redis_server_url")


@bot.d.polaris.handler_for("test_message", polaris.MessageType.CREATE)
async def on_test_message(message: polaris.Message):
    print(f"Message received: {message}")


bot.run()
```

```python
# Sending messages
from lightbulb.ext import polaris

client = polaris.Client("redis://your_redis_server_url")

msg = polaris.Message(polaris.MessageType.CREATE, "test_message", {"foo": "bar"})
await client.send_message(msg)
```

## Issues
If you find any bugs, issues, or unexpected behaviour while using the library, 
you should open an issue with details of the problem and how to reproduce if possible. 
Please also open an issue for any new features you would like to see added.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please try to ensure that documentation is updated if you add any features accessible through the public API.

If you use this library and like it, feel free to sign up to GitHub and star the project,
it is greatly appreciated and lets me know that I'm going in the right direction!

## Links
- **Repository:** [GitHub](https://github.com/tandemdude/lightbulb-ext-polaris)
