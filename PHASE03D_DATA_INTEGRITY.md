# تقرير سلامة البيانات — المرحلة 0.3.d

## القرار

**الحالة: HOLD.** تم حل مشكلة aliases ومشكلة اختيار أعمدة odds. لم يتم الانتقال إلى Backtest لأن timestamp الدقيق للquote غير متوفر، ولأن OpenFootball يحتوي عيبًا تاريخيًا موثقًا في موسم 2019-20، ولأن تكاليف التنفيذ لم تُثبت بعد.

## تشخيص المطابقة

أُنشئت قائمة كاملة للفروق في [cross_validation_discrepancies.csv](data/interim/cross_validation_discrepancies.csv)، مع تصنيف إضافي في [discrepancy_classified.csv](data/interim/discrepancy_classified.csv). أظهر تدقيق أسماء الفرق أن الفروق الشكلية نتجت من aliases مثل `Sheffield Weds` و`Peterboro` و`Nott'm Forest`. أضيفت هذه aliases إلى خط البناء.

بعد التطبيع، تطابقت أزواج الفرق بنسبة 100% في المواسم السبعة. بقيت 77 مباراة في موسم 2019-20 غير متطابقة بالتاريخ فقط. فحص مثال `Preston North End v Derby County` أظهر تاريخ `2019-07-01` في OpenFootball مقابل `2020-07-01` في football-data. صُنفت الحالات السبع والسبعون كإزاحة تاريخية قدرها 366 يومًا، ولم تُستخدم لتعديل المصدر الأساسي.

| الموسم | Football-Data | OpenFootball | تطابق التاريخ والفريق | تطابق زوج الفريق | الفروق التاريخية |
|---|---:|---:|---:|---:|---:|
| 2019-20 | 552 | 552 | 475 | 552 | 77 |
| 2020-21 | 552 | 552 | 552 | 552 | 0 |
| 2021-22 | 552 | 557 | 552 | 552 | 0 |
| 2022-23 | 552 | 557 | 552 | 552 | 0 |
| 2023-24 | 552 | 557 | 552 | 552 | 0 |
| 2024-25 | 552 | 557 | 552 | 552 | 0 |
| 2025-26 | 552 | 557 | 552 | 552 | 0 |

الخمسة سجلات الزائدة في مواسم OpenFootball اللاحقة موثقة كـ`openfootball_only`. لم تُستخدم لإضافة مباريات إلى المصدر الأساسي.

## Closing odds

يستخدم البناء الآن `PSCH` و`PSCD` و`PSCA` كـPinnacle Closing، مع fallback لكل مباراة إلى `B365CH` و`B365CD` و`B365CA`. لم تعد أعمدة `AvgCH` و`AvgCD` و`AvgCA` تُستخدم.

تم التحقق من وجود مجموعة أعمدة closing في كل ملف E1. نتجت **11,592 قيمة odds غير مفقودة**، منها 10,743 من Pinnacle و849 من Bet365 fallback. لا يملك المصدر timestamp للquote، لذلك بقي timestamp كـ`NaT`. هذا يحترم تعريف المصدر لـClosing، لكنه لا يثبت قاعدة `timestamp < kickoff` حرفيًا.

## التحقق اليدوي لعشر مباريات

تم اختيار عشر مباريات موزعة زمنيًا من موسم 2024-25. قورنت نتائج football-data وOpenFootball مع ESPN scoreboard API. تطابقت النتائج العشر من أصل عشر.

| # | المباراة | Football-Data | OpenFootball | ESPN | النتيجة |
|---:|---|---:|---:|---:|---|
| 1 | Blackburn v Derby | 4-2 | 4-2 | 4-2 | AGREE |
| 2 | Norwich v Watford | 4-1 | 4-1 | 4-1 | AGREE |
| 3 | Oxford v Derby | 1-1 | 1-1 | 1-1 | AGREE |
| 4 | Luton v Hull | 1-0 | 1-0 | 1-0 | AGREE |
| 5 | Swansea v Sunderland | 2-3 | 2-3 | 2-3 | AGREE |
| 6 | Sunderland v Portsmouth | 1-0 | 1-0 | 1-0 | AGREE |
| 7 | Bristol City v Swansea | 0-1 | 0-1 | 0-1 | AGREE |
| 8 | Swansea v Middlesbrough | 1-0 | 1-0 | 1-0 | AGREE |
| 9 | Swansea v Plymouth | 3-0 | 3-0 | 3-0 | AGREE |
| 10 | West Brom v Luton | 5-3 | 5-3 | 5-3 | AGREE |

تفاصيل الروابط والتواريخ موجودة في [manual_validation_results_2024_25.csv](data/interim/manual_validation_results_2024_25.csv).

## xG

Understat لا يدعم EFL Championship عبر مسار `soccerdata` المستخدم. لم تُختلق ملفات xG. تستخدم النسخة الحالية أهداف المباراة الحقيقية كميزات أولية لـPoisson، مع توثيق أن ذلك أضعف من نموذج يعتمد على xG.

## الاختبارات

أضيفت اختبارات `test_closing_columns_present` و`test_closing_odds_not_average` و`test_cross_validation_records_discrepancies`. يجب أن تكون نتيجة التشغيل النهائية **25/25**.

## الخلاصة

أصبح football-data مصدرًا قابلًا للتنزيل والتحقق، وأصبحت closing columns محددة رسميًا، وأصبحت الفروق مع OpenFootball مفهومة ومصنفة، كما نجح التحقق اليدوي لعشر مباريات. لا تزال الحالة `HOLD` بسبب غياب quote timestamp الصريح، وعيب تواريخ OpenFootball في 2019-20، وعدم اكتمال قرار تكاليف التنفيذ.

## References

[1]: https://www.football-data.co.uk/data.php "Football-Data UK historical football results and odds"
[2]: https://github.com/openfootball/football.json "OpenFootball football JSON data"
[3]: https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2/scoreboard "ESPN Championship scoreboard API"
