celery -A tasks.workers -Q   user_profile_crawler,comment_page_crawler,comment_crawler,repost_crawler,repost_page_crawler worker -l info --concurrency=8 -Ofair
