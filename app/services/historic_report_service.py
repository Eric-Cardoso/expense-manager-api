from app.repo.database import (
    get_connection,
    get_cursor,
    save_data,
    close_connection, 
    close_cursor
)
from app.repo.historic_report_repo import (
    get_historic_reports_data, 
    generate_historic_reports
)
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from traceback import print_exc


def generate_user_historic_reports():
    db_conn = None
    db_cursor = None

    try:
        current_date = datetime.now(tz=timezone.utc)

        anchor_date = current_date.replace(
            day=1, 
            hour=0, 
            minute=0, 
            second=0, 
            microsecond=0
        )

        initial_date_month = anchor_date - relativedelta(months=1)

        final_date_month = anchor_date - timedelta(microseconds=1)
        
        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        db_reports_data = get_historic_reports_data(
            initial_date_month=initial_date_month,
            final_date_month=final_date_month, 
            db_cursor=db_cursor
        )

        if not db_reports_data:
            return
        
        for reports_data in db_reports_data:
            reports_data['month_report'] = final_date_month.date().isoformat()
            reports_data['generated_at'] = current_date

            generate_historic_reports(
                reports_data=reports_data,
                db_cursor=db_cursor
            )
            
            save_data(db_conn=db_conn)    
    
    except Exception:
        print_exc()
        try:
            if db_conn:
                db_conn.rollback()
        except Exception:
            print_exc()

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)