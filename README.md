# Gamepigeon Scoring

See your all time win/loss/draw record in Gamepigeon in a given imessage conversation.

## How to use

Download iMessage conversations using the [imessage-exporter library](https://github.com/ReagentX/imessage-exporter) with the --format txt flag, which will save them as text files into the `imessage_export` directory. To see your gamepigeon record with a specific contact, run the following command with their phone number.

```python3 gamepigeon-scoring.py ../imessage_export/+15555555555.txt```