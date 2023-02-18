import datetime
from glassdoor import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import UniqueConstraint, ForeignKey
from slugify import slugify


class Companies(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String, nullable=False, unique=True)
    company_url = db.Column(db.String)
    ticker = db.Column(db.String)
    num_reviews = db.Column(db.Integer)
    announce_date = db.Column(db.Date)
    ipo_date = db.Column(db.Date)
    offer_status = db.Column(db.Integer)
    exchange = db.Column(db.String)
    shares = db.Column(db.Integer)
    offer_size = db.Column(db.Float)
    offer_type = db.Column(db.String)
    offer_price = db.Column(db.Float)
    pct_change_fd = db.Column(db.Float)
    pct_change_3m = db.Column(db.Float)
    last_price = db.Column(db.Float)
    num_employees = db.Column(db.Integer)
    ind_sector = db.Column(db.String)
    ind_group = db.Column(db.String)
    sic_code = db.Column(db.Integer)
    sic_name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    use_of_proceeds = db.Column(db.String)
    cstat_rev = db.Column(db.Float)
    cstat_adv_exp = db.Column(db.Float)
    cstat_rd_exp = db.Column(db.Float)
    control = db.Column(db.Integer)
    founding_year = db.Column(db.Integer)

    def __init__(self, data):
        self.company_name = data.get("company_name")
        self.company_url = data.get("company_url")
        self.ticker = data.get("ticker")
        self.num_reviews = data.get("num_reviews")
        self.announce_date = data.get("announce_date")
        self.ipo_date = data.get("ipo_date")
        self.offer_status = data.get("offer_status")
        self.exchange = data.get("exchange")
        self.shares = data.get("shares")
        self.offer_size = data.get("offer_size")
        self.offer_type = data.get("offer_type")
        self.offer_price = data.get("offer_price")
        self.pct_change_fd = data.get("pct_change_fd")
        self.pct_change_3m = data.get("pct_change_3m")
        self.last_price = data.get("last_price")
        self.num_employees = data.get("num_employees")
        self.ind_sector = data.get("ind_sector")
        self.ind_group = data.get("ind_group")
        self.sic_code = data.get("sic_code")
        self.sic_name = data.get("sic_name")
        self.city = data.get("city")
        self.state = data.get("state")
        self.use_of_proceeds = data.get("use_of_proceeds")
        self.cstat_rev = data.get("cstat_rev")
        self.cstat_adv_exp = data.get("cstat_adv_exp")
        self.cstat_rd_exp = data.get("cstat_rd_exp")
        self.control = data.get("control")
        self.founding_year = data.get("founding_year")

    def __repr__(self):
        return "<Companies(id={}, company_name={}, company_url={}, ticker={}, num_reviews={}, ipo_date={}, exchange={}, shares={}, offer_size={}, offer_type={}, offer_price={}, pct_change_fd={}, pct_change_3m={}, last_price={}, num_employees={}, ind_sector={}, ind_group={}, sic_code={}, sic_name={}, use_of_proceeds={})>".format(
            self.id,
            self.company_name,
            self.company_url,
            self.ticker,
            self.num_reviews,
            self.announce_date,
            self.ipo_date,
            self.offer_status,
            self.exchange,
            self.shares,
            self.offer_size,
            self.offer_type,
            self.offer_price,
            self.pct_change_fd,
            self.pct_change_3m,
            self.last_price,
            self.num_employees,
            self.ind_sector,
            self.ind_group,
            self.city,
            self.state,
            self.sic_code,
            self.sic_name,
            self.use_of_proceeds,
            self.cstat_rev,
            self.cstat_adv_exp,
            self.cstat_rd_exp,
            self.control,
            self.founding_year,
        )


class Reviews(db.Model):
    __tablename_ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    post_date = db.Column(db.Date, nullable=False)
    job_title = db.Column(db.String)
    current_employee = db.Column(db.Boolean)
    years_employed = db.Column(db.Float)
    review_summary = db.Column(db.String)
    pros = db.Column(db.String)
    cons = db.Column(db.String)
    advice_to_mgmt = db.Column(db.String)
    outlook = db.Column(db.Integer)
    recommends = db.Column(db.Integer)
    approves_of_ceo = db.Column(db.Integer)
    overall = db.Column(db.Integer)
    career_opportunities = db.Column(db.Integer)
    comp_benefits = db.Column(db.Integer)
    culture_values = db.Column(db.Integer)
    senior_management = db.Column(db.Integer)
    work_life_balance = db.Column(db.Integer)

    def __init__(self, data):
        self.post_date = data.get("post_date")
        self.job_title = data.get("job_title")
        self.current_employee = data.get("current_employee")
        self.years_employed = data.get("years_employed")
        self.review_summary = data.get("review_summary")
        self.pros = data.get("pros")
        self.cons = data.get("cons")
        self.advice_to_mgmt = data.get("advice_to_mgmt")
        self.outlook = data.get("outlook")
        self.recommends = data.get("recommends")
        self.approves_of_ceo = data.get("approves_of_ceo")
        self.overall = data.get("overall")
        self.career_opportunities = data.get("career_opportunities")
        self.comp_benefits = data.get("comp_benefits")
        self.culture_values = data.get("culture_values")
        self.senior_management = data.get("senior_management")
        self.work_life_balance = data.get("work_life_balance")

    def __repr__(self):
        return "<Reviews(id={}, post_date={}, job_title={}, current_employee={}, years_employed={}, review_summary={}, pros={}, cons={}, advice_to_mgmt={}, outlook={}, recommends={}, approves_of_ceo={}, overall={}, career_opportunities={}, comp_benefits={}, culture_values={}, senior_management={}, work_life_balance={})>".format(
            self.id,
            self.post_date,
            self.job_title,
            self.current_employee,
            self.years_employed,
            self.review_summary,
            self.pros,
            self.cons,
            self.advice_to_mgmt,
            self.outlook,
            self.recommends,
            self.approves_of_ceo,
            self.overall,
            self.career_opportunities,
            self.comp_benefits,
            self.culture_values,
            self.senior_management,
            self.work_life_balance,
        )


class CompanyReviews(db.Model):
    __tablename__ = "company_reviews"
    __tableargs__ = (UniqueConstraint("company_id", "review_id"),)
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    review_id = db.Column(db.Integer, nullable=False)
    db.Constraint()

    def __init__(self, data):
        self.company_id = data.get("company_id")
        self.review_id = data.get("review_id")

    def __repr__(self):
        return "<CompanyReviews(company_id={}, review_id={})>".format(
            self.company_id, self.review_id
        )


class CompanyFinancials(db.Model):
    __tablename__ = "company_financials"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, ForeignKey(Companies.id))
    ticker = db.Column(db.String)
    monthly_price_high = db.Column(db.Float)
    monthly_price_low = db.Column(db.Float)
    monthly_price_close = db.Column(db.Float)
    total_return_factor = db.Column(db.Float)
    data_date = db.Column(db.Date)
    next_data_date = db.Column(db.Date)
    ipo_date = db.Column(db.Date)
    ipo_open_price = db.Column(db.Float)
    ipo_fd_close_price = db.Column(db.Float)
    quarter = db.Column(db.Integer)
    dollar_change_quarterly = db.Column(db.Float)
    pct_change_quarterly = db.Column(db.Float)
    pct_change_from_ipo = db.Column(db.Float)
    pct_change_from_fd_close = db.Column(db.Float)

    def __init__(self, data):
        self.company_id = data.get("company_id")
        self.ticker = data.get("ticker")
        self.monthly_price_high = data.get("monthly_price_high")
        self.monthly_price_low = data.get("monthly_price_low")
        self.monthly_price_close = data.get("monthly_price_close")
        self.total_return_factor = data.get("total_return_factor")
        self.data_date = data.get("data_date")
        self.next_data_date = data.get("next_data_date")
        self.ipo_date = data.get("ipo_date")
        self.ipo_open_price = data.get("ipo_open_price")
        self.ipo_fd_close_price = data.get("ipo_fd_close_price")
        self.quarter = data.get("quarter")
        self.dollar_change_quarterly = data.get("dollar_change_quarterly")
        self.pct_change_quarterly = data.get("pct_change_quarterly")
        self.pct_change_from_ipo = data.get("pct_change_from_ipo")
        self.pct_change_from_fd_close = data.get("pct_change_from_fd_close")

    def __repr__(self):
        return "<CompanyFinancials(id={}, company_id={}, ticker={}, monthly_price_high={}, monthly_price_low={}, monthly_price_close={}, total_return_factor={}, data_date={}, next_data_date={}, ipo_date={}, ipo_open_price={}, ipo_fd_close_price={}, quarter={}, dollar_change_quarterly={}, pct_change_quarterly={}, pct_change_from_ipo={}, pct_change_from_fd_close={})>".format(
            self.id,
            self.company_id,
            self.ticker,
            self.monthly_price_high,
            self.monthly_price_low,
            self.monthly_price_close,
            self.total_return_factor,
            self.data_date,
            self.next_data_date,
            self.ipo_date,
            self.ipo_open_price,
            self.ipo_fd_close_price,
            self.quarter,
            self.dollar_change_quarterly,
            self.pct_change_quarterly,
            self.pct_change_from_ipo,
            self.pct_change_from_fd_close,
        )
