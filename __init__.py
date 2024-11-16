import re
from datetime import datetime, timedelta

from core.builtins import Bot, Image, Plain
from core.component import module
from core.utils.http import get_url
from core.scheduler import CronTrigger
from core.logger import Logger
from core.utils.i18n import Locale

API = 'https://files.mcimirror.top/api'
DEFAULT_KEY = ['clusterName', 'ownerName', 'sponsor']

mcim = module(
    bind_prefix='mcim',
    desc='{mcim.help.desc}',
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

def generate_msg(rank: str, cluster: dict, locale: Bot.MessageSession.locale = Locale('zh_cn'), show_status: bool = True):
    status = locale.t('mcim.message.cluster.online') if cluster.get('isOnline') else (locale.t('mcim.message.cluster.banned') if cluster.get('isBanned') else locale.t('mcim.message.cluster.offline'))
    fullsize = locale.t('mcim.message.cluster.full') if cluster.get('fullsize') else locale.t('mcim.message.cluster.frag')

    clusterName = cluster.get('clusterName')
    version = cluster.get('version')
    hits = cluster.get('hits')
    bytes = size_convert(cluster.get('bytes'))

    ownerName = cluster.get('ownerName')

    match rank:
        case "1":
            rank = locale.t('mcim.message.cluster.gold')
        case "2":
            rank = locale.t('mcim.message.cluster.silver')
        case "3":
            rank = locale.t('mcim.message.cluster.bronze')

    message = f'{status}{fullsize} | ' if show_status else ''
    return f'{message}{locale.t('mcim.message.top',
                                                rank=rank,
                                                clusterName=clusterName,
                                                version=version,
                                                hits=hits,
                                                bytes=bytes,
                                                ownerName=ownerName)}'

@mcim.command()
@mcim.command('status {{mcim.help.status}}')
async def status(msg: Bot.MessageSession):
    dashboard = await get_url(f'{API}/stats/center', fmt='json')

    onlines = dashboard.get('onlines')
    hits = dashboard.get('today').get('hits')
    size = size_convert(dashboard.get('today').get('bytes'))
    sources = dashboard.get('sources')
    totalFiles = dashboard.get('totalFiles')
    totalSize = size_convert(dashboard.get('totalSize'))
    startTime = datetime.fromtimestamp(dashboard.get('startTime') / 1000)
    runningTime = datetime.now() - startTime
    runningDays = runningTime.days
    runningHours, runningSeconds = divmod(runningTime.seconds, 3600)
    runningMinutes, runningSeconds = divmod(runningSeconds, 60)

    msg_list = [msg.locale.t('mcim.message.status',
                             onlines=onlines,
                             hits=hits,
                             size=size,
                             sources=sources,
                             totalFiles=totalFiles,
                             totalSize=totalSize,
                             runningDays=runningDays,
                             runningHours=runningHours,
                             runningMinutes=runningMinutes,
                             runningSeconds=runningSeconds
                             )]

    msg_list.append(
        msg.locale.t(
            'mcim.message.query_time',
            queryTime = msg.ts2strftime(
                datetime.now().timestamp(),
                timezone=False)))

    await msg.send_message(msg_list)

    cache = await get_url(f'https://mod.mcimirror.top/statistics', fmt='json')

    curseforge = cache['curseforge']
    modrinth = cache['modrinth']
    cdn = cache['file_cdn']

    msg_list = [msg.locale.t('mcim.message.cached.status',
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

@mcim.command('rank [<rank>] {{mcim.help.rank}}')
async def rank(msg: Bot.MessageSession, rank: int = 1):
    rank_list = await get_url(f'{API}/clusters', fmt='json')
    if rank < 1 or rank > len(rank_list):
        await msg.finish(msg.locale.t('mcim.message.cluster.invalid'))

    cluster = rank_list[rank - 1]

    status = msg.locale.t('mcim.message.cluster.online.detail') if cluster.get('isOnline') else (msg.locale.t('mcim.message.cluster.banned.detail') if cluster.get('isBanned') else msg.locale.t('mcim.message.cluster.offline.detail'))
    clusterName = cluster.get('clusterName')
    hits = cluster.get('hits')
    bytes = size_convert(cluster.get('bytes'))
    bandwidth = cluster.get('bandwidth')

    clusterId = cluster.get('clusterId')
    fullsize = msg.locale.t('mcim.message.cluster.full.detail') if cluster.get('fullsize') else msg.locale.t('mcim.message.cluster.frag.detail')
    proxy = msg.locale.t('mcim.message.cluster.proxy.detail') if cluster.get('isProxy') else msg.locale.t('mcim.message.cluster.nonproxy.detail')
    stat = msg.locale.t('mcim.message.cluster.masterstat')
    version = cluster.get('version')
    createdAt = msg.ts2strftime(cluster.get('createdAt')/1000, timezone=False)
    downTime = msg.ts2strftime(cluster.get('downTime')/1000, timezone=False)

    ownerName = cluster.get('ownerName')
    sponsor = cluster.get('sponsor')
    sponsorUrl = cluster.get('sponsorUrl')

    msg_list = [msg.locale.t('mcim.message.cluster.status',
                             clusterName=clusterName,
                             status=status,
                             hits=hits,
                             bytes=bytes,
                             bandwidth=bandwidth
                             )]

    await msg.send_message(msg_list)

    msg_list = [msg.locale.t('mcim.message.cluster.detail',
                             clusterId=clusterId,
                             fullsize=fullsize,
                             proxy=proxy,
                             stat=stat,
                             version=version,
                             createdAt=createdAt,
                             downTime=downTime
                             ),
                msg.locale.t('mcim.message.owner', ownerName=ownerName),
                msg.locale.t('mcim.message.sponsor', sponsor=sponsor, sponsorUrl=sponsorUrl)]

    await msg.finish(msg_list)

@mcim.command('online {{mcim.help.online}}')
async def online(msg: Bot.MessageSession):
    rank_list = await get_url(f'{API}/clusters', fmt='json')

    msg_list = []
    for (rank, cluster) in enumerate(rank_list, start=1):
        if not cluster.get('isOnline'):
            break
        msg_list.append(generate_msg(rank, cluster, msg.locale))

    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcim.message.result.empty'))

@mcim.command('banned {{mcim.help.banned}}')
async def banned(msg: Bot.MessageSession):
    rank_list = await get_url(f'{API}/clusters', fmt='json')

    msg_list = []
    for (rank, cluster) in enumerate(rank_list, start=1):
        if cluster.get('isBanned'):
            msg_list.append(generate_msg(rank, cluster, msg.locale))

    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcim.message.result.empty'))


@mcim.command('top [<rank>] {{mcim.help.top}}')
async def top(msg: Bot.MessageSession, rank: int = 10):
    rank_list = await get_url(f'{API}/clusters', fmt='json')

    if rank < 1 or rank > len(rank_list):
        await msg.finish(msg.locale.t('mcim.message.cluster.invalid'))

    msg_list = []

    for i in range(0, rank):
        try:
            msg_list.append(generate_msg(i+1, rank_list[i], msg.locale))
        except Exception:
            break

    await msg.finish(msg_list)

@mcim.command('[<keyword>] {{mcim.help.search}}')
@mcim.command('search <keyword> {{mcim.help.search}}')
async def search(msg: Bot.MessageSession, keyword: str):
    rank_list = await get_url(f'{API}/clusters', fmt='json')
    msg_list = []
    cluster_list = search_cluster(rank_list, DEFAULT_KEY, keyword)
    for (rank, cluster) in cluster_list:
        msg_list.append(generate_msg(rank, cluster, msg.locale))
    
    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcim.message.result.empty'))

@mcim.command('source {{mcim.help.source}}')
async def source(msg: Bot.MessageSession):
    source_list = await get_url(f'{API}/stats/source', fmt='json')
    msg_list = []

    for source in source_list:
        name = source.get('name')
        count = source.get('count')
        lastUpdated = source.get('lastUpdated')
        isFromPlugin = msg.locale.t('yes') if source.get('isFromPlugin') else msg.locale.t('no')
        msg_list.append(msg.locale.t('mcim.message.source',
                                     name=name,
                                     count=count,
                                     lastUpdated=lastUpdated,
                                     isFromPlugin=isFromPlugin
                                     ))

    await msg.finish(msg_list)

mcim_rss = module(
    bind_prefix='mcim_rss',
    desc='{mcim_rss.help.desc}',
    developers=['WorldHim'],
    support_languages=['zh_cn'],
)

@mcim_rss.schedule(trigger=CronTrigger.from_crontab('5 0 * * *'))
async def _():
    Logger.info('获取昨日排名...')

    yesterday = await get_url(f'{API}/stats/yesterday', fmt='json')
    yesterday_rank_list = yesterday.get('rank')
    msg_list = []

    for cluster in yesterday_rank_list:
        msg_list.append(generate_msg(cluster.get('rank'), cluster, show_status=False))

    await Bot.FetchTarget.post_message('mcim_rss', msg_list)
