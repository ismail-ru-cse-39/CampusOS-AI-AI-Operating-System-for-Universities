from app.agents.base import Agent, AgentContext, AgentResult
from app.services.demo_data import COURSE_SCHEDULES


class TimetableAgent(Agent):
    name = "timetable"
    description = "Personalized schedule generation with conflict and preference optimization"
    keywords = [
        "timetable", "schedule", "class time", "no friday", "conflict", "gap",
        "morning", "afternoon", "building",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        lower = context.message.lower()
        enrolled = context.memory.get("current_courses", [])
        enrolled_codes = {c.split()[0] for c in enrolled if c}

        candidates = [
            s for s in COURSE_SCHEDULES
            if not enrolled_codes or s["code"] in enrolled_codes or len(enrolled_codes) < 2
        ]

        if "no friday" in lower:
            candidates = [s for s in candidates if "Fri" not in s["days"]]
        if "morning" in lower:
            candidates = [s for s in candidates if int(s["start"].split(":")[0]) < 12]

        # Conflict detection
        scheduled: list[dict] = []
        conflicts: list[str] = []
        for course in candidates:
            conflict = False
            for existing in scheduled:
                shared_days = set(course["days"]) & set(existing["days"])
                if shared_days:
                    c_start = int(course["start"].replace(":", ""))
                    c_end = int(course["end"].replace(":", ""))
                    e_start = int(existing["start"].replace(":", ""))
                    e_end = int(existing["end"].replace(":", ""))
                    if c_start < e_end and e_start < c_end:
                        conflict = True
                        conflicts.append(f"{course['code']} vs {existing['code']}")
                        break
            if not conflict:
                scheduled.append(course)

        lines = ["Proposed schedule:"]
        for s in scheduled:
            days = ", ".join(s["days"])
            lines.append(
                f"  {s['code']} {s['title']}: {days} {s['start']}-{s['end']} @ {s['building']}/{s['room']}"
            )
        if conflicts:
            lines.append(f"\nResolved conflicts: {', '.join(conflicts)}")
        if not scheduled:
            lines.append("No conflict-free schedule found with your preferences. Try relaxing constraints.")

        return AgentResult(
            agent=self.name,
            message="\n".join(lines),
            metadata={"schedule": scheduled, "conflicts_resolved": conflicts},
        )
