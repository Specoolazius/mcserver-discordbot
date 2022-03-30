from mcstatus import JavaServer

server = JavaServer.lookup('sfs.ddnss.org:25565', 10)
server = JavaServer('sfs.ddnss.org', 25565)

print('got server')

status = server.status()
print(f"The server has {status.players.online} players and replied in {status.latency} ms")


print(server.status())
print(vars(server.status()))

print(server.query())

query = server.query()
print(f"The server has the following players online: {', '.join(query.players.names)}")