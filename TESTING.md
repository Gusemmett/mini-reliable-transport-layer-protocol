# Testing - Lab 3 Angus Emmett

## Tests
The following are the tests that have been run

### Test 1 -- Success
Normal testing of client and server sending over small text lines

```py
mystr = "Hello are you there"
client = MRT_client()
client.mrt_connect(SERVER, S_PORT)
client.mrt_send(mystr.encode("utf-8"))
client.mrt_disconnect()
client.mrt_close()
```

Output
```
Connected to server
Sending 1 packets
All ACKs recieved
Disconnecting...
Server Connection Closed
```

### Test 2 -- Success
Testing with a larger file
```py
	fp = open("./romeo&julliet.txt", "r")
	str_data = fp.read()
	data = str_data.encode("utf-8")
	fp.close()
	client = MRT_client()
	client.mrt_connect(SERVER, S_PORT)
	client.mrt_send(data)
	client.mrt_disconnect()
	client.mrt_close()
```

Output
```
Connected to server
Sending 138 packets
All ACKs recieved
Disconnecting...
Server Connection Closed
```

### Test 3 -- Success
Testing when server is closed then opening it
Output
```
Cannot connect to the server retrying in 5 seconds
Retrying ...
Cannot connect to the server retrying in 5 seconds
Retrying ...
Connected to server
Sending 138 packets
All ACKs recieved
Disconnecting...
Server Connection Closed
```

### Test 4 -- Success
Not sending any data
```py
	client = MRT_client()
	client.mrt_connect(SERVER, S_PORT)
	client.mrt_disconnect()
	client.mrt_close()
```

Output
```
Connected to server
Disconnecting...
Server Connection Closed
```

### Portion of server output from Tests 2 & 3
```
Give me the letter; I will look on it.
Where is the county's page, that raised the watch?
Sirrah, what made your master in this place?
PAGE
He came with flowers to strew his lady's grave;
And bid me stand aloof, and so I did:
Anon comes one with light to ope the tomb;
And by and by my master drew on him;
And then I ran away to call the watch.
PRINCE
This letter doth make good the friar's words,
Their course of love, the tidings of her death:
And here he writes that he did buy a poison
Of a poor 'pothecary, and therewithal
Came to this vault to die, and lie with Juliet.
Where be these enemies? Capulet! Montague!
See, what a scourge is laid upon your hate,
That heaven finds means to kill your joys with love.
And I for winking at your discords too
Have lost a brace of kinsmen: all are punish'd.
CAPULET
O brother Montague, give me thy hand:
This is my daughter's jointure, for no more
Can I demand.
MONTAGUE
But I can give thee more:
For I will raise her statue in pure gold;
That while Verona by that name is known,
There shall no figure at such rate be set
As that of true and faithful Juliet.
CAPULET
As rich shall Romeo's by his lady's lie;
Poor sacrifices of our enmity!
PRINCE
A glooming peace this morning with it brings;
The sun, for sorrow, will not show his head:
Go hence, to have more talk of these sad things;
Some shall be pardon'd, and some punished:
For never was a story of more woe
Than this of Juliet and her Romeo.
Exeunt
```