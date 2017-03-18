'''
ユーザ別にログ間の時間差を算出し、
時間差ごとのログ件数を集計する
'''
import pandas as pd
from datetime import datetime
import numpy as np
import math

# ログを読み込み
logs = pd.read_csv('log/log.log', index_col=None)

# 日付、時間文字列より日時値を作成
logs['dtm'] = logs[['date', 'time']].apply(lambda x: datetime.strptime(x[0] + ' ' + x[1], "%Y-%m-%d %H:%M:%S"), axis=1)
df = logs.drop(['date', 'time'], axis=1)

# ユーザ、日付でソート
df = df.sort_values(by=['user', 'dtm']).reset_index()

# 1行ずらしてユーザ、日時を追加結合
df2 = df.drop(0)
df2 = df2.append({'user': '', 'dtm': np.nan}, ignore_index=True)
df['user2'] = df2.user
df['dtm2'] = df2.dtm

# 時間差を算出
def time_diff(row):
	if row.user == row.user2:
		# ユーザが同一の場合のみ差異を算出
		return row.dtm2 - row.dtm
	return np.nan
df['time_diff'] = df.apply(time_diff, axis=1)

# 時間差をフォーマット
def format_diff(x):
	sec0 = x / np.timedelta64(1, 's')
	(minu, sec) = divmod(sec0, 60)
	(hour, minu) = divmod(minu, 60)
	if sec0 < 10:
		return '%02d:%02d:%02d秒' % (hour, minu, sec)
	elif 10 <= sec0 < 30:
		return '00:00:10~30秒'
	elif 30 <= sec0 < 60:
		return '00:00:30~60秒'
	elif 60 <= sec0 < 300:
		return '00:01:00~5分'
	elif 300 <= sec0 < 1800:
		return '00:05:00~30分'
	elif 1800 <= sec0 < 3600:
		return '00:30:00~1時間'
	elif 3600 <= sec0 < 18000:
		return '01:00:00~5時間'
	elif 18000 <= sec0:
		return '05:00:00~'
	elif math.isnan(sec0):
		return np.nan
	return 'err'
df['fmt_diff'] = df.time_diff.apply(format_diff)

# ユーザ数=時間差NaNであることを確認
# print(len(df.drop_duplicates('user')))
# print(len(df[df.fmt_diff != df.fmt_diff]))  # NaNの比較。np.nan == np.nan はFalseとなる。

# 集計、CSV出力
df.groupby('fmt_diff').size().reset_index(name='count').to_csv('output/diff_logs_time.csv')  # キー=NaNのレコードは集計されない。

