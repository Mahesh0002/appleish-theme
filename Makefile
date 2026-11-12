.PHONY: all build install uninstall doctor verify accent contrast
all: build
build:
	python3 tools/generate_gtk3.py --mode dark  --out theme/gtk-3.0/gtk.css
	python3 tools/generate_gtk3.py --mode light --out theme/gtk-3.0/gtk-light.css
	python3 tools/generate_gtk4.py --mode dark  --out theme/gtk-4.0/gtk.css
	python3 tools/generate_gtk4.py --mode light --out theme/gtk-4.0/gtk-light.css
install: build
	bash install.sh
uninstall:
	bash uninstall.sh
verify:
	python3 scripts/verify.py
doctor:
	python3 scripts/verify.py
accent:
	python3 tools/ambient_accent.py '#0077cc' --print
contrast:
	python3 tools/check_contrast.py
