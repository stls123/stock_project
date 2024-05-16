import jqdatasdk as jq
jq.auth('17614781955', '1598647asdD')
print(f"今日剩余流量：{jq.get_query_count()['spare']}")
