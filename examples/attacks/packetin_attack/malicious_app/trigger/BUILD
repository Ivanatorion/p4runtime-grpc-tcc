COMPILE_DEPS = CORE_DEPS + [
    "//apps/p4-tutorial/pipeconf:onos-apps-p4-tutorial-pipeconf",
    "@com_google_protobuf//:protobuf_java",
]

osgi_jar(
    deps = COMPILE_DEPS,
)

BUNDLES = [
    "//apps/p4-tutorial/trigger:onos-apps-p4-tutorial-trigger",
]

onos_app(
    app_name = "org.onosproject.p4tutorial.trigger",
    category = "Traffic Engineering",
    description = "Malicious App",
    included_bundles = BUNDLES,
    required_apps = [
        "org.onosproject.p4tutorial.pipeconf",
    ],
    title = "CAP Demo App Attack",
    url = "http://onosproject.org",
)
