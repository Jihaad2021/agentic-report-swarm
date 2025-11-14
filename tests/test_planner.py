from agentic_report_swarm.core.planner import Planner

planner = Planner()
plan = planner.create_plan({
    "topic": "AI in healthcare",
    "length": "short"
})

print(plan.plan_id)
for task in plan.tasks:
    print(task.id, task.type, task.deps)