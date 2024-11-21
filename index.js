const { Client, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus, NoSubscriberBehavior } = require('@discordjs/voice');
const ytdl = require('ytdl-core');
const fs = require('fs');
const path = require('path');

// Discord 봇 클라이언트 설정
const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

// Discord 토큰
const DISCORD_TOKEN = process.env.DISCORD_TOKEN_NODE;

// 봇 준비
client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}`);
});

// 명령어 처리
client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    // !play 명령어
    if (message.content.startsWith('!play')) {
        const args = message.content.split(' ');
        const url = args[1];
        if (!url || !ytdl.validateURL(url)) {
            return message.reply('유효한 유튜브 링크를 제공해주세요!');
        }

        // 음성 채널 연결
        const voiceChannel = message.member?.voice.channel;
        if (!voiceChannel) {
            return message.reply('먼저 음성 채널에 들어가야 합니다!');
        }

        const connection = joinVoiceChannel({
            channelId: voiceChannel.id,
            guildId: message.guild.id,
            adapterCreator: message.guild.voiceAdapterCreator,
        });

        // 오디오 플레이어 생성
        const player = createAudioPlayer({
            behaviors: {
                noSubscriber: NoSubscriberBehavior.Pause,
            },
        });

        // 유튜브 오디오 스트리밍
        try {
            const stream = ytdl(url, {
                filter: 'audioonly',
                quality: 'highestaudio',
                highWaterMark: 1 << 25, // 버퍼 크기 증가
            });

            const resource = createAudioResource(stream);
            player.play(resource);

            connection.subscribe(player);

            player.on(AudioPlayerStatus.Playing, () => {
                message.channel.send(`재생 중: ${url}`);
            });

            player.on(AudioPlayerStatus.Idle, () => {
                connection.destroy();
                message.channel.send('재생이 완료되었습니다.');
            });

            player.on('error', (error) => {
                console.error(error);
                connection.destroy();
                message.channel.send('재생 중 오류가 발생했습니다.');
            });
        } catch (error) {
            console.error(error);
            connection.destroy();
            message.reply('재생 중 문제가 발생했습니다.');
        }
    }

    // !leave 명령어
    if (message.content === '!leave') {
        const voiceChannel = message.member?.voice.channel;
        if (voiceChannel) {
            const connection = getVoiceConnection(voiceChannel.guild.id);
            if (connection) {
                connection.destroy();
                message.reply('음성 채널에서 나갔습니다.');
            } else {
                message.reply('봇이 음성 채널에 연결되어 있지 않습니다.');
            }
        }
    }
});

// Discord 봇 실행
client.login(process.env.DISCORD_TOKEN);
