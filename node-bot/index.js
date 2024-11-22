// .env 파일 불러오기
require('dotenv').config(); // dotenv 패키지를 사용해 .env 파일 읽기

// Discord.js 및 @discordjs/voice 패키지 불러오기
const { Client, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource } = require('@discordjs/voice');

// Discord 클라이언트 생성
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates] });

// 환경 변수에서 토큰 읽기
const DISCORD_TOKEN = process.env.DISCORD_TOKEN_NODE;

client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.content.startsWith('!play')) {
        const args = message.content.split(' ');
        const url = args[1]; // URL 가져오기
        if (!url) {
            return message.reply('URL을 입력하세요!');
        }

        if (message.member.voice.channel) {
            const connection = joinVoiceChannel({
                channelId: message.member.voice.channel.id,
                guildId: message.guild.id,
                adapterCreator: message.guild.voiceAdapterCreator,
            });

            const player = createAudioPlayer();
            const resource = createAudioResource(url);

            connection.subscribe(player);
            player.play(resource);

            player.on('error', error => {
                console.error('Error:', error.message);
            });
        } else {
            message.reply('먼저 음성 채널에 들어가야 합니다!');
        }
    }
});

// 클라이언트 로그인
client.login(DISCORD_TOKEN);
