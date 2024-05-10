try:
    import telnetlib
    print("working")
except:
    print("not working")

host="10.10.122.178"
port = 7777

tn = telnetlib.Telnet(host, port)
tn.write(b'VER?')
response = tn.read_all()
print(response)