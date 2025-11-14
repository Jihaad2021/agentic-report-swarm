from agentic_report_swarm.core.planner import simple_planner

def test_planner_creates_four_tasks():
    topic = "quantum computing"
    plan = simple_planner(topic)
    assert plan.topic == topic
    ids = [st.id for st in plan.subtasks]
    assert ids == ["t1", "t2", "t3", "t4"]
    types = [st.type for st in plan.subtasks]
    assert types == ["research", "trends", "insights", "writer"]
    # dependencies sanity
    deps = {st.id: st.depends_on for st in plan.subtasks}
    assert deps["t1"] == []
    assert deps["t2"] == ["t1"]
    assert deps["t3"] == ["t1", "t2"]
    assert deps["t4"] == ["t3"]
