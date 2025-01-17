# (C) Datadog, Inc. 2010-2016
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

# 3p
from nose.plugins.attrib import attr

# project
from checks import AgentCheck
from tests.checks.common import AgentCheckTest


@attr(requires='kong')
class TestKong(AgentCheckTest):
    CHECK_NAME = 'kong'

    CONFIG_STUBS = [
        {
            'kong_status_url': 'http://localhost:8001/status/',
            'tags': ['first_instance']
        },
        {
            'kong_status_url': 'http://localhost:8001/status/',
            'tags': ['second_instance']
        }
    ]

    BAD_CONFIG = [
        {
            'kong_status_url': 'http://localhost:1111/status/'
        }
    ]

    GAUGES = [
        'kong.total_requests',
        'kong.connections_active',
        'kong.connections_waiting',
        'kong.connections_reading',
        'kong.connections_accepted',
        'kong.connections_writing',
        'kong.connections_handled',
    ]

    def test_check(self):
        config = {
            'instances': self.CONFIG_STUBS
        }

        self.run_check_twice(config)

        # Assert metrics
        for stub in self.CONFIG_STUBS:
            expected_tags = stub['tags']
            for mname in self.GAUGES:
                self.assertMetric(mname, tags=expected_tags, count=1)


        # Assert service checks
        self.assertServiceCheck('kong.can_connect', status=AgentCheck.OK,
                                tags=['kong_host:localhost', 'kong_port:8001'], count=2)

        self.coverage_report()

    def test_connection_failure(self):
        config = {
            'instances': self.BAD_CONFIG
        }

        # Assert service check
        self.assertRaises(
            Exception,
            lambda: self.run_check(config)
        )
        self.assertServiceCheck('kong.can_connect', status=AgentCheck.CRITICAL,
                                tags=['kong_host:localhost', 'kong_port:1111'], count=1)

        self.coverage_report()
