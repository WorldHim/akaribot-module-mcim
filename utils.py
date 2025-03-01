import re
from datetime import datetime

from core.builtins import Bot
from core.utils.i18n import Locale

def size_convert(value):
    '''格式转换
    :param value: 以字节为单位的数值
    :return: 转换后的字符串（带单位）
    '''

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = 1024.0
    for item in units:
        if(value / size) < 1:
            return f'{value:.2f} {item}'
        value /= size

def search(cluster_list: dict, key_list: list, value: str):
    '''查找节点
    :param cluster_list: 节点列表
    :param key_list: 查找的键列表
    :param value: 查找的值
    :return: 查找结果列表
    '''

    result = []
    regex = re.compile(value, re.IGNORECASE)

    for (rank, cluster) in enumerate(cluster_list, start=1):
        for key in key_list:
            if regex.search(cluster.get(key)):
                result.append((rank, cluster))
                break

    return result

def generate_list(raw_rank: int, cluster: dict, locale = Locale('zh_cn'), yesterday: bool = False):
    '''生成节点排行信息
    :param raw_rank: 排名
    :param cluster: 节点信息
    :param locale: 本地化
    :param yesterday: 是否昨日排行
    :return: 生成的消息
    '''

    if not yesterday:
        status = locale.t('mcim.message.cluster.online') if cluster.get('isOnline') else (locale.t('mcim.message.cluster.banned') if cluster.get('isBanned') else locale.t('mcim.message.cluster.offline'))
        size = locale.t('mcim.message.cluster.full') if cluster.get('fullsize') else locale.t('mcim.message.cluster.frag')
        version = cluster.get('version')

    clusterName = cluster.get('clusterName')
    hits = cluster.get('hits')
    bytes = size_convert(cluster.get('bytes'))

    ownerName = cluster.get('ownerName')

    match raw_rank:
        case 1:
            rank = locale.t('mcim.message.cluster.gold')
        case 2:
            rank = locale.t('mcim.message.cluster.silver')
        case 3:
            rank = locale.t('mcim.message.cluster.bronze')
        case _:
            rank = str(raw_rank)

    if yesterday:
        return locale.t('mcim.message.yesterday.top',
                        rank=rank,
                        clusterName=clusterName,
                        hits=hits,
                        bytes=bytes,
                        ownerName=ownerName
                        )
    else:
        return f'{locale.t('mcim.message.top',
                             rank=rank,
                             status=status,
                             size=size,
                             clusterName=clusterName,
                             version=version,
                             hits=hits,
                             bytes=bytes
                         )}\n{locale.t('mcim.message.owner', ownerName=ownerName)}'

def generate_dashboard(dashboard: dict, locale = Locale('zh_cn')):
    '''生成仪表盘信息
    :param dashboard: 仪表盘信息
    :param locale: 本地化
    :return: 生成的消息
    '''

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

def generate_cache(cache: dict, locale = Locale('zh_cn')):
    '''生成缓存信息
    :param cache: 缓存信息
    :param locale: 本地化
    :return: 生成的消息
    '''

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
    '''生成节点信息
    :param msg: 消息会话
    :param cluster: 节点信息
    :return: 生成的消息
    '''

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
    proxy = msg.locale.t('mcim.message.cluster.proxy.detail') if cluster.get('isProxy') else msg.locale.t('mcim.message.cluster.local.detail')
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

def generate_source(source: dict, locale = Locale('zh_cn')):
    '''生成数据源信息
    :param source: 数据源信息
    :param locale: 本地化
    :return: 生成的消息
    '''

    name = source.get('name')
    count = source.get('count')
    lastUpdated = source.get('lastUpdated')
    isFromPlugin = locale.t('message.yes') if source.get('isFromPlugin') else locale.t('message.no')
    return locale.t('mcim.message.source',
                    name=name,
                    count=count,
                    lastUpdated=lastUpdated,
                    isFromPlugin=isFromPlugin
                    )