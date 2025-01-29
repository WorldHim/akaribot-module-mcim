from datetime import datetime

from core.builtins import Bot, Image, Plain
from core.component import module
from core.utils.http import get_url
from core.scheduler import CronTrigger, IntervalTrigger
from core.utils.i18n import Locale
from core.logger import Logger

from modules.mcim import utils, draw

API = 'https://files.mcimirror.top/api'
DEFAULT_KEY = ['clusterName', 'ownerName', 'sponsor']

TRACK_CLUSTERID = '43474a59a6436a79acd8cea0'

HITS_COLOR = '#3F51C0'
BYTES_COLOR = '#FFA500'
REJECTED_COLOR = '#FF0000'

mcim = module(
    bind_prefix='mcim',
    desc='{mcim.help.desc}',
    developers=['WorldHim'],
    recommend_modules=['mcim_rss'],
    support_languages=['zh_cn']
)

@mcim.command()
@mcim.command('status {{mcim.help.status}}')
async def status(msg: Bot.MessageSession):
    dashboard = await get_url(f'{API}/stats/center', fmt='json')

    msg_list = [utils.generate_dashboard(dashboard, msg.locale)]

    msg_list.append(
        msg.locale.t(
            'mcim.message.query_time',
            queryTime = msg.ts2strftime(
                datetime.now().timestamp(),
                timezone=False)))

    await msg.send_message(msg_list)

    cache = await get_url('https://mod.mcimirror.top/statistics', fmt='json')

    await msg.finish([utils.generate_cache(cache)])

@mcim.command('rank [<rank>] {{mcim.help.rank}}')
async def rank(msg: Bot.MessageSession, rank: int = 1):
    rank_list = await get_url(f'{API}/clusters', fmt='json')
    if rank < 1 or rank > len(rank_list):
        await msg.finish(msg.locale.t('mcim.message.cluster.invalid'))

    cluster = rank_list[rank - 1]
    banner = cluster.get('sponsorBanner')
    msg_list = utils.generate_cluster(msg, cluster)

    await msg.send_message(msg_list[0])
    await msg.send_message(msg_list[1])
    try:
        await msg.finish([Image(banner)])
    except Exception:
        await msg.finish(msg.locale.t('mcim.message.banner.failed'))

@mcim.command('online {{mcim.help.online}}')
async def online(msg: Bot.MessageSession):
    rank_list = await get_url(f'{API}/clusters', fmt='json')

    msg_list = []
    for (rank, cluster) in enumerate(rank_list, start=1):
        if not cluster.get('isOnline'):
            break
        msg_list.append(utils.generate_list(rank, cluster, msg.locale))

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
            msg_list.append(utils.generate_list(rank, cluster, msg.locale))

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
            msg_list.append(utils.generate_list(i+1, rank_list[i], msg.locale))
        except Exception:
            break

    await msg.finish(msg_list)

@mcim.command('[<keyword>] {{mcim.help.search}}')
@mcim.command('search <keyword> {{mcim.help.search}}')
async def search(msg: Bot.MessageSession, keyword: str):
    rank_list = await get_url(f'{API}/clusters', fmt='json')
    msg_list = []
    cluster_list = utils.search(rank_list, DEFAULT_KEY, keyword)
    for (rank, cluster) in cluster_list:
        msg_list.append(utils.generate_list(rank, cluster, msg.locale))

    if msg_list:
        await msg.finish(msg_list)
    else:
        await msg.finish(msg.locale.t('mcim.message.result.empty'))

@mcim.command('source {{mcim.help.source}}')
async def source(msg: Bot.MessageSession):
    source_list = await get_url(f'{API}/stats/source', fmt='json')
    msg_list = []

    for source in source_list:
        msg_list.append(utils.generate_source(source))

    await msg.finish(msg_list)

@mcim.command('yesterday [--full] {{mcim.help.yesterday}}',
              options_desc={'--full': '{mcim.help.option.full}'})
async def yesterday(msg: Bot.MessageSession = None):

    if msg is None:
        locale = Locale('zh_cn')
        Logger.info('获取昨日统计信息...')
    else:
        locale = msg.locale
        full = msg.parsed_msg.get('--full', False)

    try:
        yesterday = await get_url(f'{API}/stats/yesterday', status_code=200, fmt='json')

        hits = yesterday.get('total').get('hits')
        size = utils.size_convert(yesterday.get('total').get('bytes'))

        msg_list = [locale.t('mcim.message.yesterday.status',
                         hits=hits,
                         size=size
                         )]
        yesterday_rank_list = yesterday.get('rank')

        for cluster in yesterday_rank_list:
            msg_list.append(utils.generate_list(cluster.get('rank'), cluster, yesterday=True))

    except Exception:
        msg_list = [locale.t('mcim.message.yesterday.failed')]

    if msg is None:
        await Bot.FetchTarget.post_message('mcim_rss', msg_list)
    else:
        await msg.send_message(msg_list)

    msg_list = []

    hits_list = yesterday.get('hits')
    hits_label = locale.t('mcim.message.yesterday.hits')

    bytes_list = yesterday.get('bytes')
    bytes_label = locale.t('mcim.message.yesterday.bytes')

    if full:
        hits_figure = draw.single_figure(hits_list, hits_label, HITS_COLOR)
        msg_list.append(Image(hits_figure))

        bytes_figure = draw.single_figure(draw.byte2GB(bytes_list), bytes_label, BYTES_COLOR)
        msg_list.append(Image(bytes_figure))

        rejected_list = yesterday.get('rejected')
        rejected_label = locale.t('mcim.message.yesterday.rejected')
        rejected_figure = draw.single_figure(rejected_list, rejected_label, REJECTED_COLOR)
        msg_list.append(Image(rejected_figure))
    else:
        figure = draw.complex_figure(hits_list, hits_label, HITS_COLOR,
                                     draw.byte2GB(bytes_list), bytes_label, BYTES_COLOR)
        msg_list.append(Image(figure))

    if msg is None:
        await Bot.FetchTarget.post_message('mcim_rss', msg_list)
    else:
        await msg.finish(msg_list)

mcim_rss = module(
    bind_prefix='mcim_rss',
    desc='{mcim_rss.help.desc}',
    developers=['WorldHim'],
    recommend_modules=['mcim'],
    support_languages=['zh_cn']
)

@mcim_rss.schedule(trigger=CronTrigger.from_crontab('5 0 * * *'))
async def notify():
    await yesterday()

mcim_cluster_rss = module(
    bind_prefix='mcim_cluster_rss',
    desc='{mcim_cluster_rss.help.desc}',
    developers=['WorldHim'],
    recommend_modules=['mcim'],
    support_languages=['zh_cn']
)

# @mcim_cluster_rss.schedule(IntervalTrigger(seconds=300))
# async def cluster_notify():
#     cluster = await get_url(f'{API}/clusters/{TRACK_CLUSTERID}', fmt='json')
