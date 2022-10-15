serve:
	hugo -D serve

publish:
	@echo "Building..."
	@HUGO_ENV=production hugo --minify
	@echo "Uploading..."
	@lftp ftp.rotarytriaditsa.org -e "set ftp:ssl-allow off; lcd public; mirror -R; exit"

.PHONY: \
  serve publish

