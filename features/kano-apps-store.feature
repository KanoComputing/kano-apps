#
# kano-apps-store.feature
#
# Copyright (C) 2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Behave feature file to make sure Kano Apps is working well
# on the new COPPA compliant Kano App Store
#
# NOTE: Please set the following line under /etc/hosts
#
#   127.0.0.1       world-staging.kano.me
#   127.0.0.1       world.kano.me
#   127.0.0.1       api.kano.me
#   127.0.0.1       api-staging.kano.me
#
# This is to make sure kano-apps is not using the obsolete URLs.
#

Feature: Kano Apps Integrates corectly with the new App Store

        Scenario: Kano Apps console mode works well
        Given that I am in Classic Mode
        When I call kano-apps install whatsapp non-gui
        Then I see whatsapp installed

        Scenario: Kano Apps GUI opens correctly
        Given that I am in Classic Mode
        When I start kano-apps
        Then I see the main dialog with no authentication

        Scenario: Kano Apps GUI opens correctly
        Given that I am in Classic Mode
        When I start kano-apps to install njam
        Then I see the main dialog requesting password
