COMPILE_DEPS = CORE_DEPS + [
    "//apps/p4-tutorial/pipeconf:onos-apps-p4-tutorial-pipeconf",
    "@com_google_protobuf//:protobuf_java",
]

osgi_jar(
    deps = COMPILE_DEPS,
)

BUNDLES = [
    "//apps/p4-tutorial/int:onos-apps-p4-tutorial-int",
]

onos_app(
    app_name = "org.onosproject.p4tutorial.int",
    category = "Traffic Engineering",
    description = "Inband Telemetry Use Case",
    included_bundles = BUNDLES,
    required_apps = [
        "org.onosproject.p4tutorial.pipeconf",
    ],
    title = "Inband Telemetry INT",
    url = "http://onosproject.org",
)
