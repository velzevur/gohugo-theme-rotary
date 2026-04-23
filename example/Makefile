WEBP_QUALITY ?= 80

serve:
	hugo -D serve

minify-css:
	@python3 themes/gohugo-theme-rotary/scripts/minify_css.py \
		--content public \
		public/dist/css/rotary.css \
		public/dist/css/photoswipe.css

publish:
	@echo "Building..."
	@HUGO_ENV=production hugo --minify
	@$(MAKE) minify-css
	@echo "Uploading..."
	@python3 scripts/deploy_changed.py public ftp.rotarytriaditsa.org

publish-dry-run:
	@echo "Building..."
	@HUGO_ENV=production hugo --minify
	@$(MAKE) minify-css
	@python3 scripts/deploy_changed.py --dry-run public ftp.rotarytriaditsa.org

publish-baseline:
	@echo "Building..."
	@HUGO_ENV=production hugo --minify
	@$(MAKE) minify-css
	@python3 scripts/deploy_changed.py --mark-deployed public ftp.rotarytriaditsa.org

published_tags:
	python3 scripts/stats.py  --language $(lang) --published --count_tags

count:
	python3 scripts/stats.py  --language $(lang) --published --count

find_tag:
	python3 scripts/list_tags.py -l $(lang) -m find -t "$(tag)"

translate:
	python3 scripts/stats.py  --language $(lang) --to_translate $(count)

add: 
	python3 scripts/new.py  --language $(lang) --file add.md

images-webp:
	@echo "Converting images to .webp (quality $(WEBP_QUALITY))..."
	@for dir in content static; do \
		[ -d "$$dir" ] || continue; \
		find "$$dir" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 | \
		while IFS= read -r -d '' file; do \
			out="$${file%.*}.webp"; \
			echo "$$file -> $$out"; \
			if cwebp -quiet -q "$(WEBP_QUALITY)" "$$file" -o "$$out"; then \
				rm "$$file"; \
			else \
				echo "Failed to convert $$file" >&2; \
				exit 1; \
			fi; \
		done; \
	done

.PHONY: \
  serve minify-css publish publish-dry-run publish-baseline images-webp
