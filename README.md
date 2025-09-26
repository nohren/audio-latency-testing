# Python install

`conda env create -f environment.yml`

If more stuff gets added
`conda env update -f environment.yml`

# Outbound Calling

```bash
python outbound/outbound.py --to <phone_numbers> --bot_id <assistantId>

```

example

```bash
python outbound/outbound.py --to +14158675309,+15109035768,+19102565467

```

# Coinbase scam numbers

Pool:

```bash
"4303527550,866-388-9572,(929) 528-5446,860-841-4500,+1 855 771 0354,202-552-1545,+13057221291,+1 (866) 866-8301,+1 (785) 314-0617,(234) 752-8571,+44 20 3322 2243,+1 (626) 310-4118"
```

Non-Functional:

Possibly Functional:

```bash
"+1 (860) 841 4500,+1 (205) 325 9594,+1(845) 576-1001,+19297099520,+13322703566,+17023485561,+18702019634,+1 870 201 9473"

```

# audio-latency-testing

Download tampermonkey extension in chrome. Create a new script and copy/paste vapi-latency.js.
