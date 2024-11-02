import re
from datetime import datetime

from core.builtins import Bot, Image, Plain
from core.component import module
from core.utils.http import get_url

API = 'https://files.mcimirror.top/93AtHome'
DEFAULT_KEY = ['clusterName', 'ownerName', 'sponsor']

mcimstatus = module(
    bind_prefix='mcimstatus',
    desc='{mcimstatus.help.desc}',
    alias='mcim',
    developers=['WorldHim'],
    support_languages=['zh_cn'],
)

def size_convert(value):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = 1024.0
    for i in range(len(units)):
        if(value / size) < 1:
            return '%.2f%s' % (value, ' ' + units[i])
        value /= size

def search_cluster(cluster_list: dict, key_list: list, value: str):
    result = []
    regex = re.compile(value, re.IGNORECASE)

    for (rank, cluster) in enumerate(cluster_list, start=1):
        for key in key_list:
            if regex.search(cluster.get(key)):
                result.append((rank, cluster))
                break

    return result

def generate_msg(locale: Bot.MessageSession.locale, rank: int, cluster: dict):
    status = locale.t('mcimstatus.message.cluster.online') if cluster.get('isOnline') else (locale.t('mcimstatus.message.cluster.banned') if cluster.get('isBanned') else locale.t('mcimstatus.message.cluster.offline'))
    fullsize = locale.t('mcimstatus.message.cluster.full') if cluster.get('fullsize') else locale.t('mcimstatus.message.cluster.frag')

    clusterName = cluster.get('clusterName')
    version = cluster.get('version')
    hits = cluster.get('hits')
    traffic = size_convert(cluster.get('traffic'))

    ownerName = cluster.get('ownerName')
    return f'{status}{fullsize} | {locale.t('mcimstatus.message.top',
                                                rank=rank,
                                                clusterName=clusterName,
                                                version=version,
                                                hits=hits,
                                                traffic=traffic,
                                                ownerName=ownerName)}'


@mcimstatus.command()
@mcimstatus.command('status {{mcimstatus.help.status}}')
async def status(msg: Bot.MessageSession):
    dashboard = await get_url(f'{API}/centerStatistics', fmt='json')
    cache = await get_url(f'https://mod.mcimirror.top/statistics', fmt='json')
    onlines = dashboard.get('onlines')
    hits = dashboard.get('today').get('hits')
    size = size_convert(dashboard.get('today').get('bytes'))
    totalFiles = dashboard.get('totalFiles')
    totalSize = size_convert(dashboard.get('totalSize'))

    msg_list = [msg.locale.t('mcimstatus.message.status',
                             onlines=onlines,
                             hits=hits,
                             size=size,
                             totalFiles=totalFiles,
                             totalSize=totalSize
                             )]

    msg_list.append(
        msg.locale.t(
            'mcimstatus.message.query_time',
            queryTime = msg.ts2strftime(
                datetime.now().timestamp(),
                timezone=False)))

    await msg.send_message(msg_list)

    curseforge = cache['curseforge']
    modrinth = cache['modrinth']
    cdn = cache['file_cdn']

    msg_list = [msg.locale.t('mcimstatus.message.cached.status',
                             time=msg.ts2strftime(datetime.now().timestamp(),timezone=False),
                             cf_mod=curseforge['mod'],
                             cf_file=curseforge['file'],
                             cf_fingerprint=curseforge['fingerprint'],
                             mr_project=modrinth['project'],
                             mr_version=modrinth['version'],
                             mr_file=modrinth['file'],
                             cdn_file=cdn['file']
                             )]

    await msg.finish(msg_list)

@mcimstatus.command('rank [<rank>] {{mcimstatus.help.rank}}')
async def rank(msg: Bot.MessageSession, rank: int = 1):
    rank_list = await get_url(f'{API}/rank', fmt='json')
    if rank < 1 or rank > len(rank_list):
        await msg.finish(msg.locale.t('mcimstatus.message.cluster.invalid'))

    cluster = rank_list[rank - 1]

    status = msg.locale.t('mcimstatus.message.cluster.online.detail') if cluster.get('isOnline') else (msg.locale.t('mcimstatus.message.cluster.banned.detail') if cluster.get('isBanned') else msg.locale.t('mcimstatus.message.cluster.offline.detail'))
    clusterName = cluster.get('clusterName')
    hits = cluster.get('hits')
    traffic = size_convert(cluster.get('traffic'))
    bandwidth = cluster.get('bandwidth')

    clusterId = cluster.get('clusterId')
    fullsize = msg.locale.t('mcimstatus.message.cluster.full.detail') if cluster.get('fullsize') else msg.locale.t('mcimstatus.message.cluster.frag.detail')
    version = cluster.get('version')
    createdAt = msg.ts2strftime(cluster.get('createdAt'), timezone=False)
    downTime = msg.ts2strftime(cluster.get('downTime'), timezone=False)

    ownerName = cluster.get('ownerName')
    sponsor = cluster.get('sponsor')
    sponsorUrl = cluster.get('sponsorUrl')

    msg_list = [msg.locale.t('mcimstatus.message.cluster.status',
                             clusterName=clusterName,
                             status=status,
                             hits=hits,
                             traffic=traffic,
                             bandwidth=bandwidth
                             )]

    await msg.send_message(msg_list)

    msg_list = [msg.locale.t('mcimstatus.message.cluster.detail',
                             clusterId=clusterId,
                             fullsize=fullsize,
                             version=version,
                             createdAt=createdAt,
                             downTime=downTime
                             ),
                msg.locale.t('mcimstatus.message.owner', ownerName=ownerName),
                msg.locale.t('mcimstatus.message.sponsor', sponsor=sponsor, sponsorUrl=sponsorUrl)]

    await msg.finish(msg_list)

@mcimstatus.command('online {{mcimstatus.help.online}}')
async def online(msg: Bot.MessageSession):
    rank_list = await get_url(f'{API}/rank', fmt='json')

    msg_list = []
    for (rank, cluster) in enumerate(rank_list, start=1):
        if not cluster.get('isOnline'):
            break
        msg_list.append(generate_msg(msg.locale, rank, cluster))

    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcimstatus.message.result.empty'))

@mcimstatus.command('banned {{mcimstatus.help.banned}}')
async def banned(msg: Bot.MessageSession):
    rank_list = await get_url(f'{API}/rank', fmt='json')

    msg_list = []
    for (rank, cluster) in enumerate(rank_list, start=1):
        if cluster.get('isBanned'):
            msg_list.append(generate_msg(msg.locale, rank, cluster))

    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcimstatus.message.result.empty'))


@mcimstatus.command('top [<rank>] {{mcimstatus.help.top}}')
async def top(msg: Bot.MessageSession, rank: int = 10):
    rank_list = await get_url(f'{API}/rank', fmt='json')

    if rank < 1 or rank > len(rank_list):
        await msg.finish(msg.locale.t('mcimstatus.message.cluster.invalid'))

    msg_list = []

    for i in range(0, rank):
        try:
            msg_list.append(generate_msg(msg.locale, i+1, rank_list[i]))
        except Exception:
            break

    await msg.finish(msg_list)

@mcimstatus.command('search <keyword> {{mcimstatus.help.search}}')
async def search(msg: Bot.MessageSession, keyword: str):
    rank_list = await get_url(f'{API}/rank', fmt='json')
    msg_list = []
    cluster_list = search_cluster(rank_list, DEFAULT_KEY, keyword)
    for (rank, cluster) in cluster_list:
        msg_list.append(generate_msg(msg.locale, rank, cluster))
    
    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcimstatus.message.result.empty'))
