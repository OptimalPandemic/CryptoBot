DESTDIR=
SYSCONFDIR=/etc
PREFIX=/usr
SYSTEMCTL:=$(shell which systemctl)

init:
	pip3 install -r requirements.txt
test:
	py.test tests
build:
	pyinstaller main.py --name cryptobot --onefile
install:
	if test -e "$(DESTDIR)$(PREFIX)/bin"; then install -m0644 dist/cryptobot $(DESTDIR)$(PREFIX)/bin/cryptobot; fi
	if test -x "$(SYSTEMCTL)" && test -d "$(DESTDIR)$(SYSCONFDIR)/systemd/system"; then install -m0644 scripts/cryptobot.systemd $(DESTDIR)$(SYSCONFDIR)/systemd/system/cryptobot.service && $(SYSTEMCTL) daemon-reload; fi
	if test -e "$(DESTDIR)$(SYSCONFDIR)/systemd/system/cryptobot.service" && test ! -e "$(DESTDIR)$(SYSCONFDIR)/systemd/system/multi-user.target.wants/cryptobot.service"; then $(SYSTEMCTL) enable cryptobot.service; fi

.PHONY: init test build