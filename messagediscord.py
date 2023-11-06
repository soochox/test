import discord

# 봇 토큰을 설정합니다. 디스코드 개발자 포털에서 얻을 수 있습니다.
TOKEN = '여러분의 봇 토큰을 여기에 넣으세요'

# 디스코드 클라이언트를 생성합니다.
client = discord.Client()

# 봇이 준비되었을 때 실행될 이벤트 핸들러를 정의합니다.
@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

    # 원하는 채널의 ID를 입력하세요.
    channel_id = 1234567890
    channel = client.get_channel(channel_id)

    # 메시지를 보낼 내용을 입력하세요.
    message_content = '안녕하세요, 디스코드 봇 메시지입니다!'
    
    # 메시지를 보냅니다.
    await channel.send(message_content)

# 봇을 실행합니다.
client.run(TOKEN)
