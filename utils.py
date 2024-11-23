import re
from datetime import datetime

from core.builtins import Bot
from core.utils.i18n import Locale

def size_convert(value):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = 1024.0
    for i in range(len(units)):
        if(value / size) < 1:
            return '%.2f%s' % (value, ' ' + units[i])
        value /= size

def search(cluster_list: dict, key_list: list, value: str):
    result = []
    regex = re.compile(value, re.IGNORECASE)

    for (rank, cluster) in enumerate(cluster_list, start=1):
        for key in key_list:
            if regex.search(cluster.get(key)):
                result.append((rank, cluster))
                break

    return result

def generate_list(raw_rank: int, cluster: dict, locale: Bot.MessageSession.locale = Locale('zh_cn'), show_status: bool = True):
    status = locale.t('mcim.message.cluster.online') if cluster.get('isOnline') else (locale.t('mcim.message.cluster.banned') if cluster.get('isBanned') else locale.t('mcim.message.cluster.offline'))
    fullsize = locale.t('mcim.message.cluster.full') if cluster.get('fullsize') else locale.t('mcim.message.cluster.frag')

    clusterName = cluster.get('clusterName')
    version = cluster.get('version')
    hits = cluster.get('hits')
    bytes = size_convert(cluster.get('bytes'))

    ownerName = cluster.get('ownerName')

    rank = ''
    match raw_rank:
        case 1:
            rank = locale.t('mcim.message.cluster.gold')
        case 2:
            rank = locale.t('mcim.message.cluster.silver')
        case 3:
            rank = locale.t('mcim.message.cluster.bronze')
        case _:
            rank = str(raw_rank)

    message = f'{status}{fullsize} | ' if show_status else ''
    return f'{message}{locale.t('mcim.message.top',
                                rank=rank,
                                clusterName=clusterName,
                                version=version,
                                hits=hits,
                                bytes=bytes,
                                ownerName=ownerName
                                )}'

def generate_dashboard(dashboard: dict, locale: Bot.MessageSession.locale = Locale('zh_cn')):
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

    return locale.t('mcim.message.status',
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
                    )

def generate_cache(cache: dict, locale: Bot.MessageSession.locale = Locale('zh_cn')):
    curseforge = cache['curseforge']
    modrinth = cache['modrinth']
    cdn = cache['file_cdn']

    return locale.t('mcim.message.cached.status',
                    cf_mod=curseforge['mod'],
                    cf_file=curseforge['file'],
                    cf_fingerprint=curseforge['fingerprint'],
                    mr_project=modrinth['project'],
                    mr_version=modrinth['version'],
                    mr_file=modrinth['file'],
                    cdn_file=cdn['file']
                    )

def generate_cluster(msg: Bot.MessageSession, cluster: dict):
    message = []

    status = msg.locale.t('mcim.message.cluster.online.detail') if cluster.get('isOnline') else (msg.locale.t('mcim.message.cluster.banned.detail') if cluster.get('isBanned') else msg.locale.t('mcim.message.cluster.offline.detail'))
    clusterName = cluster.get('clusterName')
    hits = cluster.get('hits')
    bytes = size_convert(cluster.get('bytes'))
    bandwidth = cluster.get('bandwidth')

    message.append([msg.locale.t('mcim.message.cluster.status',
                            clusterName=clusterName,
                            status=status,
                            hits=hits,
                            bytes=bytes,
                            bandwidth=bandwidth
                            )])

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

    message.append([msg.locale.t('mcim.message.cluster.detail',
                                 clusterId=clusterId,
                                 fullsize=fullsize,
                                 proxy=proxy,
                                 stat=stat,
                                 version=version,
                                 createdAt=createdAt,
                                 downTime=downTime
                                 ),
                    msg.locale.t('mcim.message.owner', ownerName=ownerName),
                    msg.locale.t('mcim.message.sponsor', sponsor=sponsor, sponsorUrl=sponsorUrl
                    )])

    return message

def generate_source(source: dict, locale: Bot.MessageSession.locale = Locale('zh_cn')):
    name = source.get('name')
    count = source.get('count')
    lastUpdated = source.get('lastUpdated')
    isFromPlugin = locale.t('yes') if source.get('isFromPlugin') else locale.t('no')
    return locale.t('mcim.message.source',
                    name=name,
                    count=count,
                    lastUpdated=lastUpdated,
                    isFromPlugin=isFromPlugin
                    )
        
