# Deployment statement / 运行说明

## Operational deployment

The project maintainer provided the following deployment facts on 2026-08-26:

| Item | Confirmed scope |
|---|---|
| Operational use began | March 2026 |
| Subsequent development | Continued iteration after launch; current public snapshot prepared in August 2026 |
| Location | Shanghai, China |
| Site type | Corporate industrial park parking facility |
| Administrators | 3 |
| Managed parking spaces | 286 |
| Modules in use | All application modules included in the public edition |
| Code relationship | As of the current public snapshot, the public repository and the on-site application use the same application source code |
| Confirming organization | The corporate industrial park management office |

“All application modules” refers to administrator authentication, user management, parking-space management, parking records, reservations, points and credit records, system configuration, rule-based scheduling and historical traffic baseline functions, and the browser management dashboard.

March 2026 is the start of operational use, not the date of the current snapshot. The running system was subsequently refined through later iterations. The current-code statement describes the relationship between the public and on-site application source **as of this public snapshot**; it does not claim that the August release existed unchanged at launch.

The specific company name, site address, staff identities and contact details are not published in this repository. The confirming organization is identified by role to protect site and personnel privacy.

## Public-package boundary

- As of this public snapshot, the public application source is the same application source used on site.
- Site secrets, administrator credentials, personal information, the live database, network configuration and runtime operational records are not included.
- The confirmed operational capacity is 286 parking spaces. The public initializer preserves the same total capacity but uses example identifiers and generated users rather than live site records.
- Operational use does not by itself establish a measured efficiency improvement, machine-learning accuracy or a performance benchmark. Those claims require separately authorized and reproducible evidence.

## 中文说明

项目维护者于 2026 年 8 月 26 日确认：系统于 **2026 年 3 月**在**上海一处企业园区停车场**开始实际使用，现场有 **3 名管理员**，管理 **286 个车位**，公开版所包含的应用模块均已使用。投入使用后，系统继续进行后续迭代。截至当前公开快照，当前公开仓库与当前现场应用使用相同的应用源代码；这不表示 8 月版本在 3 月时已以完全相同形态存在。

实际使用情况可由该**企业园区管理办公室**确认。为保护企业与人员隐私，公开仓库不披露企业名称、具体地址、联系人、账号凭据、个人信息、现场数据库或原始运营记录。
