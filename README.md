# Apps Homepage

Landing page listing the Manhattan apps people can open. A Flask API
(`api/index.py`) serves the app catalog — each entry's live version and
last-updated date are fetched dynamically from the app's own deployment —
and a static `index.html` renders it as a grid of tiles.

## Current apps (21)

| Name | URL | Description |
|---|---|---|
| Check In Kiosk | https://checkinkiosk.vercel.app | Check-in kiosk application for appointment management |
| Inspection | https://inspection-wms.vercel.app | Inspection app with updates and photos |
| Facility Address Update | https://facilityaddresses.vercel.app | Tool for managing and identifying facility addresses |
| LPN Lock / Unlock | https://lpnlock.vercel.app | Application for locking and unlocking License Plate Numbers (LPNs) |
| MHE Console | https://mhe-console.vercel.app | Material Handling Equipment console for monitoring and managing MHE operations |
| Order Generator | https://ordergenerator.vercel.app | Generate and manage orders with bulk import capabilities and order validation |
| Appointment Date Update | https://update-appt.vercel.app | Tool for updating appointment dates and managing appointment schedules |
| Item Generator Gallery | https://itemgenerator-gallery.vercel.app | Generate product items, download images, and bulk import to Manhattan WMS |
| Proof of Delivery | https://proofofdelivery.vercel.app | Capture delivery confirmations and proof-of-delivery details |
| Cycle Count Import | https://cyclecount.vercel.app | Import and manage cycle count data |
| Work Order Update | https://work-order-update.vercel.app | Update Work Order item descriptions from the Item Master |
| Dispatch *(under development)* | https://dispatch-manh.vercel.app | Trip filtering and driver self-assignment for Manhattan TMS |
| Manual Dispatch Request *(under development)* | https://dispatch-request.vercel.app | Create Transportation Orders and dispatch trips manually |
| Appointment Calendar | https://scheduleappt.vercel.app | Five-day grid for visualizing hourly appointment availability |
| Driver Pickup | https://driver-pickup.vercel.app | Signature capture for truck drivers during pickup |
| Item Update *(under development)* | https://item-update.vercel.app | Update Item Master fields and item image |
| Flowthrough | https://flowthrough.vercel.app | ASN-driven replenishment allocation — preview algorithms and create facility orders |
| Item Copy | https://item-copy.vercel.app | Copy an existing Item Master record and create a new item with updated ID and description |
| Supplier Enablement | https://supplierenablement.vercel.app | Create ASNs from POs and generate LPNs against Manhattan WMS |
| Receiving Workbench | https://receivingworkbench.vercel.app | Receive against an ASN from a warehouse dock — full, partial, or all-lines receiving |
| VAS Execution | https://vasexecution.vercel.app | Look up and complete assigned VAS services on an oLPN |

This table is generated from `APPS_CONFIG` in `api/index.py` — that file is
the source of truth; update it first, then this table, when apps are
added, removed, or renamed.

## Adding or removing an app

Edit the `APPS_CONFIG` list in `api/index.py`: each entry needs `id`,
`name`, `url`, `vercel_project`, and `description`; `version`/`lastUpdated`
are always `None` in source (fetched live at request time). Set
`under_development: True` to flag a tile as still in progress.

Only list apps that are actively maintained in the `work` folder — apps
whose source has moved elsewhere (e.g. to a `Sandbox` folder) or that have
been superseded by another app should be removed here too.

## Running locally

```
npm install
pip install -r requirements.txt
vercel dev
```
