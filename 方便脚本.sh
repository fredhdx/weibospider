celery -A tasks.workers -Q  comment_page_crawler,comment_crawler,repost_crawler,repost_page_crawler worker -l info --concurrency=8 -Ofair
