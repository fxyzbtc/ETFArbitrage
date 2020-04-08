print(__file__,__name__,__package__)
from flask.views import MethodView, View
from flask import render_template

from pandas import DataFrame as DF

from .. import utils
from .. import (app, db)
from .models import Indice
from .models import PePb

class Query(MethodView):
    def get(self):
        return 'get all/individual pe/table/plotly'
    def post(self):
        return 'insert pe'
    def put(self):
        return 'update pe'
    def delete(self):
        return 'delete pe'

class SyncIndice(View):
    def dispatch_request(self):

        lxr = utils.LiXingRener()
        if lxr.login(app.config['LXR_USERNAME'], app.config['LXR_PASSWORD']):
            import json
            indice = json.loads(lxr.getIndice())
            entries = []
            for item in indice:
                entry = Indice(**{k.lower():item[k] for k in lxr.indice_fields})
                entries.append(entry)
            
            Indice.query.delete()
            db.session.add_all(entries)
            db.session.commit()
            return {'message': 'indice updated'}
        else:
            return {'message': 'updating indice failed'}

class SyncPePb(View):
    def dispatch_request(self, stockid, *args, **kwargs):
        lxr = utils.LiXingRener()
        if lxr.login(app.config['LXR_USERNAME'], app.config['LXR_PASSWORD']):
            import json
            app.logger.info('pulling {}'.format(stockid))
            pepb = lxr.getPePb(stockid) #<id>
            # change timeout nginx/uwsgi

            # update pepb reocrds
            entries = []
            for entry in pepb['entries']:
                _entry = PePb(**entry)
                entries.append(_entry)

            # update pepb 
            db.session.query(PePb).filter(PePb.stockid==stockid).delete()
            #PePb.query.filter(PePb.stockid==1000000000995).delete()
            db.session.bulk_save_objects(entries)
            
            # update indice static
            db.session.query(Indice).filter(Indice.stockid==stockid).update(pepb['static'])
            db.session.commit()
            return {'message': 'pulled pepb data of {}'.format(stockid)}
        else:
            return {'message': 'failed to login data source'}

class ListIndice(View):
    def dispatch_request(self, *args, **kwargs):
        result    = []
        
        fields    = ['name', "stockcode", 'pb_latestval', 'pb_latestvalpos',
                    'pe_ttm_latestval', 'pe_ttm_latestvalpos',
                    'pb_chanceval', 'pb_medianval', 'pb_riskval',
                    'pe_ttm_chanceval', 'pe_ttm_medianval', 'pe_ttm_riskval',
                    'pb_maxval', 'pb_maxvaldate', 'pb_minval','pb_minvaldate',
                    'pe_ttm_maxval', 'pe_ttm_maxvaldate', 'pe_ttm_minval','pe_ttm_minvaldate',
                    'launchdate', 'stockid',]
        #companies = session.query(SomeModel).options(load_only(*fields)).all()
        #q = db.session.query(Indice).add_columns(*fields).all()
        q = db.session.query(Indice).add_columns(*fields).all()
        for item in q:
            result.append(item._asdict())
        
        df = DF(result)
        return render_template('mod_pe/indice.html', table=df.to_html(classes=['table', 'table-striped', 'table-bordered', 'dataTable'], table_id="datatable"))