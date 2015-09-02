PickleServ
==========

This code serves two purposes:
- The primary purpose is an example of the security risk posed by unpickling
  untrusted input.
- The secondary purpose is as a drop-dead simple Python object transfer system,
  **provided you are in a secure network**.  Obviously, the above security
  limitation comes first.

It's pretty fun to try out.  You need three terminal windows running Python:

In the first one (server), do:

```python
import pickleserv
pickleserv.run_pickle_server()
```

In the second one (sending client), do:

```python
import pickleserv
pickleserv.send([some object here], 'your name here')
```

In the third one (receiving client), do:

```python
import pickleserv
pickleserv.recv('your name here')
```

The third terminal window should output the object you sent from the second
terminal window.  You should also see the object get print out by the server
when it receives it.


Security Issue
--------------

In one of your client Python instances, do the following code:

```python
pickleserv.server_command('ls -l')
```

Check your server window, you should see the output of `ls -l`, followed by a
traceback.  The server just executed the bash command you typed in on the
client, because `pickle` could run code during the unpickling process.  So,
like, be careful when you unpickle stuff.  Class dismissed!
