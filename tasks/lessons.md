# Lessons learned

Append a short bullet when a correction or incident reveals a durable rule for this project.

## Template

- **Date / context**: …
- **What went wrong**: …
- **Rule going forward**: …

---

## Entries

- **API tests & i18n**: Do not assert exact English scheme names when the API translates recommendation labels to the user’s language (e.g. Hindi); assert structure or fuzzy markers instead.
- **Dependencies**: Pin and edit packages in **repo root `requirements.txt` only**; `backend/requirements.txt` must stay a **`-r ../requirements.txt`** mirror so Docker/SAM and local installs stay aligned.
- **Subagent recovery**: If a prior run reports execution error, re-run via a focused subagent, then manually review and tighten relevance logic before final verification.
- **Security in frontend rendering**: Never interpolate API strings directly into `insertAdjacentHTML`; always escape text and validate URLs (allow only `http/https`) before rendering links.
