# Fabric deployment checklist

- [ ] Workspace, capacity, and environment naming approved.
- [ ] Managed credentials configured outside source control.
- [ ] Eventstream routes raw events to Eventhouse and Lakehouse Bronze.
- [ ] Contract compatibility check accepts the deployed schema version.
- [ ] Bronze/Silver/Gold tables have documented owner and grain.
- [ ] Quarantine and reconciliation queries have been validated.
- [ ] Direct Lake semantic model relationships and DAX measures validated.
- [ ] KQL dashboard/querysets validated against live test data.
- [ ] Activator alerts reviewed for false-positive behavior.
- [ ] Rollback and retention procedure documented before production use.
